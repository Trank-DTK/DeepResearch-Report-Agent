# 智绘研报图文报告智能生成系统 V1.0

> **DeepResearch 式长图文报告生成 Agent**：输入一个研究问题，系统自动完成「规划 → 多源联网检索 → 证据整理 → 分章撰写 → 图表生成与校验 → 报告合成」，输出一份**带图表、带引用来源**的图文研究报告（Markdown / HTML / 浏览器打印 PDF）。

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-blue">
  <img alt="UI" src="https://img.shields.io/badge/UI-Streamlit-ff4b4b">
  <img alt="LLM" src="https://img.shields.io/badge/LLM-OpenAI%20%E5%85%BC%E5%AE%B9%20%7C%20Ollama-4c72b0">
  <img alt="Lines" src="https://img.shields.io/badge/Source-~2300%20lines%20%2F%2044%20files-green">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-lightgrey">
</p>

---

## ✨ 特性

| 能力 | 说明 |
|---|---|
| 🧠 **手写 Agent 内核** | 不使用 LangChain/LangGraph，自行实现"规划 + JSON 动作循环"（`thought/action/args`），含步数上限、未知动作回灌纠错、工具异常隔离、章节级熔断 |
| 🔎 **多源检索** | 网页检索（Tavily / DuckDuckGo）＋**学术检索（OpenAlex，DOI 优先、按被引量排序）**，检索器可插拔 |
| 🛡 **三级降级链** | 网页抓取 trafilatura → BeautifulSoup → 搜索摘要，任何网络异常都不中断流程 |
| 💾 **双层缓存** | 检索结果缓存 + 网页正文缓存（离线重跑几乎零成本，省 API 额度） |
| 📊 **FDV 图表范式** | 参考 Multimodal DeepResearcher (AAAI 2026)：**Find（提取数据）→ Draw（绘图）→ Verify（图文一致性校验）**；图型由代码按数据形态决策（占比→环形图、趋势→折线、并列→柱状/条形），配色与图注自动生成 |
| ✅ **报告自检器** | 合成后自动体检：引用完整性、引用越界（防幻觉）、图表一致性、章节结构、字数达标，输出 ✅/⚠️/❌ 清单 |
| 🔌 **插件化扩展** | `src/providers/` 目录自动发现：新增检索器 / 模型渠道 / 校验器只需复制模板改约 30 行 |
| 🔄 **双渠道模型** | 同一套 OpenAI 兼容适配层，本地（Ollama / LM Studio）与在线 API（DeepSeek 等）配置即切换 |
| 🖥 **Web 界面** | Streamlit：输入问题 → 实时进度日志 → 报告预览（含图）→ 一键下载 Markdown / HTML |
| 📉 **回归样例集** | `examples/questions.json` + `scripts/regression.py`，记录章节数/字数/自检结果/耗时，改动代码后可量化对比报告质量 |

## 🖼 效果预览

> 截图位于 `docs/images/`（主界面、运行日志、质量自检、图文报告预览）。

| 主界面 | 运行进度 | 图文报告 |
|---|---|---|
| ![主界面](docs/images/01_main.png) | ![运行日志](docs/images/02_running.png) | ![报告预览](docs/images/03_report.png) |

## 🏗 架构

```
┌──────────────────────────────────────────────────────────────┐
│ UI 层      src/ui/app.py        Streamlit（输入/配置/进度/预览/下载）│
├──────────────────────────────────────────────────────────────┤
│ 应用层     src/agent/runner.py  端到端流水线（CLI 与 GUI 共用）      │
│           src/agent/core.py    手写 Agent 内核（JSON 动作循环）     │
│           src/agent/planner.py 章节提纲规划                        │
├──────────────────────────────────────────────────────────────┤
│ 能力层     src/retrieval/  检索器·抓取器·双层缓存                  │
│           src/report/     FDV 图表·TextVerifier·合成·HTML·自检器    │
├──────────────────────────────────────────────────────────────┤
│ 基础设施   src/llm/        OpenAI 兼容统一客户端（重试+退避）        │
│           src/providers/  插件注册与自动发现（检索器/模型/校验器）     │
└──────────────────────────────────────────────────────────────┘
```

## 📁 目录结构

```
deepresearch-report-agent/
├── config.yaml            # 主配置（模型渠道、检索器、图表、报告参数）
├── requirements.txt
├── src/
│   ├── agent/             # core(动作循环) / planner / tools / state / runner
│   ├── llm/               # OpenAI 兼容客户端（chat / chat_json 容错重试）
│   ├── providers/         # 插件目录：tavily / ddgs / openalex / arxiv / openai_compatible
│   ├── report/            # chart(FDV) / verify / auto_chart / synthesizer / render / checker
│   ├── retrieval/         # search / fetch(降级链) / cache(两级缓存)
│   ├── ui/                # Streamlit 界面
│   └── utils/             # 配置加载、项目根定位
├── scripts/               # CLI 入口、冒烟测试、回归脚本、软著源程序导出
├── examples/              # 回归问题集与历史产物
└── docs/                  # PRD / 架构 / 排期 / 截图
```

## 🚀 快速开始

```bash
# 1) 环境（conda 或 venv 均可）
conda create -n zhyb python=3.11 -y && conda activate zhyb
pip install -r requirements.txt

# 2) 配置密钥
cp .env.example .env        # 填入 TAVILY_API_KEY；如需在线模型再填 DEEPSEEK_API_KEY / GLM_API_KEY

# 3) 可选：本地模型（8GB 显存可跑）
ollama pull qwen3:8b

# 4) 启动 Web 界面
streamlit run src/ui/app.py        # 浏览器打开 http://localhost:8501
```

命令行方式（无界面、便于脚本化）：

```bash
python scripts/m2_report.py "大模型推理加速的主流技术路线有哪些？"
# 产物：data/outputs/report_<hash>.md 与同名 .html（图片 base64 内嵌，单文件自包含）

python scripts/regression.py --limit 1     # 跑回归样例集（记录 stats）
```

## ⚙️ 配置要点（`config.yaml`）

| 配置项 | 说明 |
|---|---|
| `llm.provider` | 固定 `openai_compatible`；渠道由 `base_url/model/api_key_env` 决定 |
| `llm.timeout` | 建议 180（本地模型长上下文较慢） |
| `search.provider` | `tavily`（默认）或 `ddgs`（免费兜底） |
| `search.extra_providers` | `["openalex"]` 启用学术检索；设为 `[]` 关闭 |
| `chart.verify_mode` | `text`（默认，任意模型可用的图文一致性校验） |
| `report.min_words` | 报告正文字数下限（自检器使用） |

**切换模型渠道示例**：

```yaml
# 本地 Ollama（开发调试，免费）
llm:
  base_url: http://localhost:11434/v1
  model: qwen3:8b
  api_key_env: ""

# 在线 DeepSeek（终稿/演示，输出更稳定）
llm:
  base_url: https://api.deepseek.com
  model: deepseek-chat
  api_key_env: DEEPSEEK_API_KEY
```

## 📄 输出示例

一次运行（"大模型推理加速的主流技术路线有哪些？"）的典型产物：

- **报告结构**：研究摘要 → 目录 → 5~6 章正文（每章含 `####` 小节与 `[n]` 引用标注）→ 文末统一参考文献（含论文 DOI）
- **图表**：自动生成 2~6 张图表（柱状/条形/折线/环形），均已通过图文一致性校验
- **质量自检**：`6✓ / 0⚠ / 0✗` 级别的体检清单
- **文件**：`data/outputs/report_*.md`、`report_*.html`（浏览器打开可 Ctrl+P 打印为 PDF）

## ⚠️ 已知限制

1. **本地小模型输出稳定性有边界**：qwen3:8b 单次 JSON 输出的稳定上限约 450 字，超长章节由"质量闸门 + 回灌重试 + 保底成稿"兜底，仍可能个别章节失败；**正式演示建议切换在线模型**。
2. **部分站点不可达**：知乎/华为论坛等返回 403、Google/YouTube 等在本网络环境超时——降级链会以搜索摘要兜底，报告会如实体现证据强度。
3. **不生成 PDF 文件**：按设计由 HTML 经浏览器打印导出，以避免中文字体与排版依赖。
4. **arXiv 接口需自备网络环境**：默认学术源为 OpenAlex（国内直连可用），arXiv 适配器保留但可能不可达。

## 🗺 路线图（v2.0 方向）

- [ ] 本地文档 RAG（支持上传资料作为证据源）
- [ ] 报告评测模块（引用真实性抽查、图文一致性量化指标）
- [ ] VisionVerifier：接入视觉模型对图表做像素级一致性校验
- [ ] FastAPI + Vue 前端、PyInstaller 单文件分发
- [ ] 多轮追问与报告增量更新

## 📜 软件著作权

本软件已按 **「智绘研报图文报告智能生成系统 V1.0」** 提交计算机软件著作权登记（个人独立开发）。

## 🙏 致谢

本项目的设计参考了以下研究工作：

- **Multimodal DeepResearcher** (AAAI 2026) — FDV（Find-Draw-Verify）图文报告生成范式
- **DeepReporter** — 长报告生成中的规划与撰写策略
- **TVIR** 相关长图文报告生成工作 — 文本-图表一致性思路

## 📄 License

MIT License（详见 `LICENSE`）。
