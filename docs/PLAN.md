# 项目计划 — 智绘研报 V1.0（4 周 + 缓冲）

> 对应决策 Q12。假设每日投入 3~5 小时；实际投入变化时告诉我，我实时重排。

## 1. 排期总览

| 周 | 主题 | 里程碑 |
|---|---|---|
| 第 1 周（D1~D7） | 地基：环境/LLM/检索/抓取 | M1：CLI 搜索→抓取→证据库 |
| 第 2 周（D8~D15） | Agent 内核 + 纯文本报告 | M2：CLI 完整报告 |
| 第 3 周（D16~D21） | FDV 图表 + 自检 + GUI 首版 | M3：GUI 端到端（**GUI 红线：第 3 周内可跑**） |
| 第 4 周（D22~D28） | 打磨 + 软著材料 + 发布 | tag v1.0 + GitHub + 软著提交 |

## 2. 每日任务卡

### 第 1 周
- **D1 环境**：git init；创建 venv；`pip install -r requirements.txt`；`.env` 填 key；
  验证 `python -c "import openai, httpx, trafilatura, matplotlib, streamlit"` 全通。
  验收：骨架可跑、依赖可 import。
- **D2~D3 LLM 层**：`src/llm/client.py`（OpenAI 兼容）+ `src/providers/registry.py` +
  `src/providers/llm_openai_compatible.py` 模板 + JSON 容错重试。
  验收：Ollama 本地 与 DeepSeek 在线 双渠道调通。
- **D4~D5 检索层**：`src/retrieval/search.py` 接口 + `src/providers/tavily_search.py` +
  `src/providers/ddgs_search.py` + 查询缓存。
  验收：双检索器可切换、缓存命中生效。
- **D6 Fetcher**：`src/retrieval/fetch.py` 三级降级。验收：抓真实网页出干净正文。
- **D7 M1**：`src/agent/state.py` 证据库落盘；CLI 串联"查询词→搜索→抓取→归档"。
  验收：一个查询词产出结构化证据 JSON。

### 第 2 周
- **D8~D9 Planner**：`src/agent/planner.py` 问题→提纲 JSON（3~6 章）。
- **D10~D12 内核（重头戏）**：`src/agent/core.py` JSON 动作循环 + `src/agent/tools.py`。
- **D13~D14 撰写与合成**：write_section 带引用标注；Synthesizer 出 Markdown。
- **D15 M2**：CLI 端到端第一份纯文本报告（提纲+正文+引用清单）。

### 第 3 周
- **D16~D17 FDV 闭环**：`src/report/chart.py`（Find→Draw）+ `src/report/verify.py`
  TextVerifier；matplotlib 中文字体配置。验收：报告出现 1~2 张校验过的图表。
- **D18 渲染**：`src/report/render.py` MD→HTML（CSS 模板 + base64 图）。
- **D19 自检器**：`src/report/checker.py` + 引用真实性校验。
- **D20 GUI**：`src/ui/app.py` Streamlit（输入/后台线程/进度/预览/下载）。
- **D21 M3**：GUI 端到端出带图带引用报告；截图存档。

### 第 4 周
- **D22 VisionVerifier**：`src/report/verify.py` 视觉校验 + `src/providers/verifier_glm.py`
  （GLM-5.3-Flash，可选开启）。
- **D23 GUI 打磨**：配置页（LLM/检索器/校验器切换）+ token 成本统计。
- **D24~D25 回归**：`examples/questions.json` 3 题 + `scripts/regression.py`；
  修 bug；软著界面截图。
- **D26 软著材料**：`scripts/export_source.py`（前后各 30 页/每页 50 行自动切页）+
  说明书初稿（带截图）→ `soft_copyright/`。
- **D27 发布**：README 完善 + LICENSE(MIT) + 密钥泄露检查 → `git tag v1.0` → push GitHub。
- **D28 提交**：软著在线提交，拿到受理号；项目复盘。

## 3. 波动应对策略（你提到"实际执行波动大"，这是预案）

1. **时间盒原则**：每张任务卡有验收标准，**达标即停，不追求完美**；
2. **缓冲池**：每里程碑后留 1 天机动；总硬性上限 **35 天**（软著提交日顺延即可，3~4 个月拿证不受影响）；
3. **砍刀优先级**（落后时按序砍，绝不砍核心）：
   ① VisionVerifier（D22）→ ② GUI 打磨项（D23）→ ③ 回归样例 3 题减为 2 题（D24）→ ④ 说明书初稿压缩（D26）。
   **永远保留**：核心闭环（FR-1~FR-7）+ 自检器 + 软著材料生成 + tag v1.0；
4. **卡壳规则**：任何任务卡连续 2 小时无进展 → 立刻贴代码问我，不硬耗；
5. **每日投入波动**：今天没空就跳，明天优先补"里程碑最近"的任务。

## 4. 风险清单

| 风险 | 概率 | 应对 |
|---|---|---|
| Tavily 免费额度提前耗尽 | 中 | 缓存兜底 + 一键切 DDGS；调试期用本地模型 |
| DDGS 限流 | 中 | 自动降级用搜索摘要；降低并发 |
| 本地小模型 JSON 输出不稳 | 高 | 容错重试 + prompt 约束 + 必要时临时换在线模型验证逻辑 |
| 网页反爬/超时 | 高 | 三级降级链 + 10s 超时 + 并发限制 |
| matplotlib 中文乱码 | 高 | D16 任务卡专门配置中文字体（SimHei/Microsoft YaHei） |
| 进度落后 | 中 | 见"砍刀优先级" |
| 软著材料补正 | 低 | 材料从 tag v1.0 生成、截图与功能对应、自查清单 |
| 密钥误传 GitHub | 低 | `.env` 进 .gitignore + D27 全仓扫描检查 |

## 5. 协作方式

- 每日开工：我给你**当天任务卡**（文件清单 + 接口约定 + 验收标准 + 参考提示）；
- 你写代码，卡住随时贴代码给我，我做 code review；
- 每里程碑：停下复盘 30 分钟（跑通演示 + 问题清单 + 下阶段调整）；
- 所有关键决策继续更新 `AGENTS.md`。

## 6. GitHub 规范

- 分支：`main`；里程碑/发布用 tag（M1/M2/M3、v1.0）；
- Commit 前缀：`feat/fix/docs/chore/refactor`；
- README 结构：简介 → 特性 → 效果图 → 架构图 → 快速开始 → 配置 → 示例报告 → 路线图 → 致谢；
- LICENSE：MIT；`.env`、`data/`、`soft_copyright/` 绝不提交。

## 7. 软著材料清单（D26 交付）

1. `soft_copyright/源代码_前后各30页.docx`（脚本自动切页生成）；
2. `soft_copyright/说明书.docx`（含 GUI 截图，功能与代码对应）；
3. `soft_copyright/申请表信息清单.md`（名称/版本/完成日期/发表日期/著作权人）。
