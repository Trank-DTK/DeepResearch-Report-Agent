# 架构设计 — 智绘研报 V1.0

## 1. 总体架构（分层）

```
┌─────────────────────────────────────────────────────────┐
│  UI 层      src/ui/            Streamlit                │
│            输入/配置/进度/预览/下载/自检展示              │
├─────────────────────────────────────────────────────────┤
│  应用层     src/agent/core.py  手写 Agent 内核            │
│             Planner(一次规划) → 每章 JSON 动作循环        │
│             → Synthesizer(汇总合成) → SelfChecker(自检)   │
├─────────────────────────────────────────────────────────┤
│  能力层     src/retrieval/   src/report/   src/utils/     │
│            检索器+抓取器     图表管线    缓存/日志/配置     │
│                          Markdown→HTML 渲染               │
├─────────────────────────────────────────────────────────┤
│  基础设施   src/llm/           OpenAI 兼容统一客户端       │
│             src/providers/     插件注册机制(自动发现)      │
├─────────────────────────────────────────────────────────┤
│  数据        data/cache  data/outputs  data/logs          │
└─────────────────────────────────────────────────────────┘
```

依赖方向自上而下：UI → 应用 → 能力 → 基础设施。

## 2. 目录结构

```
deepresearch-report-agent/
├── AGENTS.md / README.md / LICENSE / .gitignore / .env(.example)
├── config.yaml               # 主配置（渠道/参数选择）
├── requirements.txt
├── docs/                     # PRD / ARCHITECTURE / PLAN
├── src/
│   ├── llm/                  # LLM 客户端：OpenAI 兼容适配 + JSON 容错重试
│   ├── retrieval/            # SearchProvider 接口、tavily/ddgs 实现、Fetcher 降级链、缓存
│   ├── agent/                # core(循环状态机)/planner/tools/state
│   ├── report/               # 图表管线、Verifier(文本/视觉)、MD→HTML 渲染、自检器
│   ├── ui/                   # Streamlit 页面
│   ├── utils/                # 配置加载、日志、token 统计
│   └── providers/            # 插件目录：自动发现（LLM/检索器/抓取器/校验器模板）
├── examples/                 # 3 个回归问题 + 历史输出
├── scripts/                  # regression.py 回归脚本
└── data/                     # cache/outputs/logs（gitignore）
```

## 3. 核心模块职责

| 模块 | 文件 | 职责 | 接口 |
|---|---|---|---|
| LLM 统一客户端 | `src/llm/client.py` | 按配置构造 OpenAI 兼容 client；chat() 统一入口；JSON 输出解析+重试 | `chat(messages) -> str`、`chat_json(...) -> dict` |
| 插件注册机制 | `src/providers/registry.py` | 扫描 providers 目录，按基类收集已注册类，按名称实例化 | `get_provider(kind, name, cfg)` |
| 检索器 | `src/retrieval/search.py` | SearchProvider 抽象；Tavily/DDGS 实现；结果缓存 | `search(query, max_results) -> list[SearchResult]` |
| 抓取器 | `src/retrieval/fetch.py` | 三级降级：trafilatura→bs4→摘要 | `fetch(url) -> str` |
| 证据库 | `src/agent/state.py` | RunState：提纲/证据/章节/引用表；落盘与恢复 | dataclass + JSON |
| Agent 内核 | `src/agent/core.py` | JSON 动作循环：解析 thought/action/args → 调工具 → 回填 → 判断终止 | `run(question) -> Report` |
| 规划器 | `src/agent/planner.py` | 问题 → 章节提纲 JSON | `plan(question) -> Outline` |
| 工具表 | `src/agent/tools.py` | search/fetch/extract_chart_data/draw_chart/verify/write_section/finalize 注册 | 名称→函数映射 |
| FDV 管线 | `src/report/chart.py` | Find→Draw→Verify 循环，重画上限 3 轮 | `fdv_pipeline(section) -> Chart` |
| 校验器 | `src/report/verify.py` | TextVerifier（默认）/ VisionVerifier | `verify(chart, text) -> verdict` |
| 渲染 | `src/report/render.py` | MD→HTML（CSS+base64 图）；文件导出 | `render(md, charts) -> html_path` |
| 自检器 | `src/report/checker.py` | 引用完整性/防幻觉/图表一致/结构/字数 | `check(report) -> list[CheckItem]` |
| UI | `src/ui/app.py` | Streamlit；后台线程跑 Agent + 轮询进度 | — |

## 4. 关键设计

### 4.1 插件注册机制

```python
# src/providers/registry.py（示意）
REGISTRY = {"search": {}, "llm": {}, "fetcher": {}, "verifier": {}}

def register(kind, name):
    def deco(cls): REGISTRY[kind][name] = cls; return cls
    return deco

def discover():  # 扫描 src/providers/*.py 并 import
    ...

# 用户新增检索器：复制模板 → 继承基类 → 加 @register("search", "my_search") → 改 30 行
```

配置 `config.yaml` 中按名称选择（如 `search.provider: my_search`），实例化时从 REGISTRY 取类。

### 4.2 Agent JSON 动作循环

每章循环的 LLM 输出约定：

```json
{"thought": "……", "action": "search|fetch|extract_chart_data|draw_chart|verify|write_section|finalize", "args": {}}
```

- 解析失败自动重试 2 次 → 仍失败记警告、按安全默认动作继续；
- 步数上限 `agent.max_steps_per_section`（默认 8）防死循环；
- 状态全部在 `RunState` 中，支持中断后从落盘恢复（对长任务 UI 至关重要）。

### 4.3 图表生成管线

```
Find:  LLM 从本章证据库提取 {数据表: [{label, value, unit, source_url}]}
Draw:  程序用 matplotlib 按数据表画图（bar/line/pie，按数据形态自动选择）→ PNG
Verify:
  TextVerifier(默认):   LLM 对照"数据表 ↔ 章节文字 ↔ 图标题"检查一致性
  VisionVerifier(可选): 把 PNG + 章节文字发给 VLM 视觉校验
  → 不一致: 生成修正意见 → 修正数据表/重画（≤3 轮）
```

### 4.4 自检器

`checker.py` 规则校验（不依赖 LLM，稳定）：
引用编号有定义；正文引用的 URL 属于 证据库（**否则 警告 标红**）；图表占位符有对应 PNG 且通过 FDV 校验；章节数与提纲一致；字数 ≥ 2000。结果展示在 UI 并写入日志。

## 5. 数据模型（简版）

- `Outline`: title, sections[{id, question, keywords}]
- `SearchResult`: url, title, snippet, source_provider
- `Evidence`: url, title, content, section_id, fetched_at
- `Chart`: data_table, png_path, verify_status, verify_rounds, verdict
- `Section`: section_id, markdown, citations[n], charts[]
- `Report`: markdown, html_path, references[], selfcheck_result, stats{tokens, cost}


## 6. 运行环境

**开发/运行环境**

- 硬件：x86_64 PC，内存 ≥ 8GB（本地模型 8GB 显存可跑 qwen3:8b）；
- 软件：Windows 10/11 64 位；Python 3.10+；依赖见 `requirements.txt`；
- 网络：需互联网连接；可选本地模型服务 Ollama/LM Studio；
- 密钥：Tavily API Key（检索，可选 DDGS 免密）、LLM API Key（本地部署时无需）。


## 8. v2.0 展望

本地文档 RAG、FastAPI+Vue 前端、自动评测（LLM-as-judge）、PyInstaller 打包、
多轮对话、LangGraph 可选内核迁移。
