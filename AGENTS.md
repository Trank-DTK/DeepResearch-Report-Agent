# AGENTS.md — 项目上下文注入文件

> 本文件是项目的持久记忆。任何 AI 助手在开始工作前都应先阅读本文件。
> 每次确认一项关键决策后，必须同步更新本文件（特别是「已确认决策」与「待决策问题树」）。

## 一、项目总览

- **项目方向**：DeepResearch 式「长图文报告生成 Agent」——输入一个研究问题，输出一份带图、带引用来源的长报告。
- **项目定位（三重目标）**：
  1. 锻炼工程实践能力（用户工程能力几乎为 0，这是首要目标）；
  2. 未来科研的「实验平台」（用户后续要在 DeepResearch Agent 方向做科研、发论文，本项目框架要设计成可复现论文、可替换模块的形态）；
  3. 申请软件著作权 + 发布到 GitHub。
- **工作目录**：`E:\项目\deepresearch-report-agent`（项目根目录；骨架与 docs/ 已建）

## 二、用户画像（重要，影响所有技术选型）

- 准大三计算机专业学生。
- **强项**：Python。
- **薄弱项**：前端（HTML/CSS/JS/TS/Vue 都学得很浅，且基本遗忘）；前后端连接（Ajax/Django/FastAPI 很浅）。
- **AI Agent 背景**：了解 langchain、ReAct Agent、RAG、VLM、skill、MCP、harness，均为浅层了解。
- **正在阅读的论文**：TVIR、DeepReporter 等 DeepResearch Agent 长图文报告生成相关论文（科研文献阅读阶段，尚未开始实验）。
- 学习能力正常，但需要保姆级、可执行的指导。

## 三、已确认决策

| 编号 | 决策 | 结论 | 确认时间 |
|---|---|---|---|
| Q1 | 项目方向 | 选 A：DeepResearch 式长图文报告生成 Agent；以「为未来科研做实验平台」为隐性架构目标 | 已确认 |
| Q2 | 软著时间 | 普通通道 3~4 个月拿证可接受，不加急；项目完成后立即提交，先拿受理通知书 | 已确认 |
| Q3 | 持续记忆 | 在 `E:\项目\deepresearch-report-agent\AGENTS.md` 维护上下文注入文件，AI 助手每轮关键决策后更新 | 已确认 |
| Q4 | v1.0 功能边界 | 核心闭环：问题输入→ReAct 规划→联网检索→证据整理→章节撰写（带引用标注）→图表生成→报告合成（Markdown+HTML）→Web 界面→配置与日志。**明确不做**：本地文档 RAG、多轮追问、用户系统、重前端、自动评测框架（v2.0 再做） | 已确认 |
| Q4a | 图表生成范式 | 采用 Multimodal DeepResearcher (AAAI 2026) 的 **FDV 范式**：Find（从证据提取数据）→ Draw（matplotlib 绘图）→ Verify（校验图文一致性，错误则修正重画）。该论文开源，后续科研可参考 | 已确认 |
| Q4b | LLM 双渠道 | 用户可选：①本地部署（Ollama / LM Studio）②在线 API Key。统一走 OpenAI 兼容接口层，两种渠道共享同一套适配器 | 已确认 |
| Q4c | 检索工具可插拔 | 默认 Tavily（用户已注册，有免费额度），架构上做成可插拔检索器，备选 DuckDuckGo 等免费方案 | 已确认 |
| Q5 | 报告形态 | 权威格式 Markdown（带引用标注、图表占位符）→ 转 HTML（内置 CSS 模板，图表 PNG 转 base64 内嵌）→ 浏览器打印 PDF。统一报告骨架：标题/研究概要/目录/各章(正文+引用+图表)/参考来源清单。**中文报告**。不直接生成 PDF | 已确认 |
| Q6 | 检索与抓取 | 检索器：Tavily（默认，额度保护靠本地缓存）+ DuckDuckGo（免费兜底）。抓正文：httpx + trafilatura，降级链：trafilatura→beautifulsoup→搜索摘要。检索策略：每子问题 2~3 个改写查询词×前5条，≥3 条有效证据，不足则换词重搜或如实标注"证据不足" | 已确认 |
| Q6a | 插件注册机制 | `src/providers/` 目录自动发现：抽象基类 + 注册装饰器，用户复制模板改 30 行即可接入新检索器；**同一约定复用于 LLM 提供者与抓取器**（三个扩展点一套机制），软著说明书可写"支持自定义扩展"卖点 | 已确认 |
| Q7 | LLM 选型 | 统一 OpenAI 兼容接口：本地 Ollama/LM Studio（base_url 直连）+ 在线 DeepSeek（推荐默认，便宜中文强）等多家（用户已有多个 key）。8GB 显存 → 本地推荐 qwen3:8b。小模型输出加 JSON 容错重试。成本控制：调试用本地免费、token 预算上限、全程缓存 | 已确认 |
| Q7a | FDV 视觉校验 | v1.0 内置双 Verifier（沿用插件机制）：TextVerifier（默认，纯文本对照校验，任何模型可用）+ **VisionVerifier（可选，真·VLM 看图校验）**。VisionVerifier 默认推荐 **GLM-5.3-Flash**（智谱 BigModel，免费/极低价多模态；OpenRouter 的 ox-alpha 即其匿名马甲，现身份已揭晓）。校验失败自动修正重画，上限 2~3 轮 | 已确认 |
| Q8 | Agent 框架 | **v1.0 手写最小 Agent 内核，不用 LangChain/LangGraph**（理由：学习价值第一、软著原创性、框架 API 变动快）。形态：Planner 一次规划生成章节提纲 → 每子问题 JSON 动作循环（thought/action/args，search/fetch/extract_chart_data/draw_chart/verify/write_section/finalize）→ Synthesizer 汇总合成。JSON 解析失败自动重试 2 次，仍失败记警告继续。目录 `src/agent/`：core.py（循环状态机）/planner.py/tools.py/state.py，全接口化，日后可平滑迁移 LangGraph。用户曾手写 ReAct，有基础 | 已确认 |
| Q9 | 前端形态 | **Streamlit**（纯 Python、零前端负担、进度流式展示利于软著截图、Markdown 渲染报告、内嵌 HTML 预览）。长任务用"后台线程跑 Agent + 界面轮询进度"模式。用户学过一点 Streamlit。FastAPI+Vue 留 v2.0 | 已确认 |
| Q10 | 质量与评测 | v1.0 内置：①报告自检器（合成后自动跑：引用完整性、防幻觉第一道闸[正文 URL 必须存在于证据库]、图表一致性、结构完整性，产出自检报告显示于界面）②引用真实性校验（去重/格式/可选可达性抽查）。`examples/` 放 3 个典型问题 + `scripts/regression.py` 回归脚本。**不做** LLM-as-judge 自动评分（留给科研阶段，是创新切入点） | 已确认 |
| Q11 | 名称与冻结 | **软件全称：智绘研报图文报告智能生成系统 V1.0**；GitHub 仓库名 `deepresearch-report-agent`（README 用中文全称）。冻结策略：第4周末 git tag v1.0 → 软著材料全部从该 tag 生成 → 之后 main 继续迭代。申请表：开发完成日期=v1.0 冻结日、首次发表日期=GitHub 公开日、著作权人=个人/独立开发 | 已确认 |
| Q12 | 排期 | 28 天排期（详见 `docs/PLAN.md`）：W1 地基/LLM/检索/抓取 → W2 Agent 内核+纯文本报告 → W3 FDV+自检+GUI（红线：第3周内 GUI 可跑）→ W4 视觉校验+打磨+回归+软著材料+发布。**波动预案**：时间盒+每里程碑1天缓冲+砍刀优先级（视觉校验→GUI打磨→样例减为2题，核心闭环永不砍）；卡壳2小时即求助。**执行模式**：任务卡队列制、不打卡、日历软约束（软著提交目标≤开工后6周，超8周则评估砍需求） | 已确认 |
| Q13 | 科研衔接 | 已定（详见 `docs/ARCHITECTURE.md` §6）：论文组件↔可替换模块映射表（planner/retrieval/core/FDV/verifier/checker/examples）；预留 judge.py 空接口与本地 RAG 检索器模板两个科研钩子；消融实验=换模块实现不改框架 | 已确认 |
| Q14 | 运行环境 | 已定（详见 `docs/ARCHITECTURE.md` §7）：Windows 10/11 + Python 3.10+ + 联网；本地模型可选（8GB 显存可跑 qwen3:8b）；v1.0 不做打包，说明书按"源码+pip+streamlit 启动"描述；PyInstaller 留 v2.0 | 已确认 |

## 四、硬性约束

1. **周期 ≤ 1 个月**（从开工到可提交软著的 v1.0）。
2. 项目后续发布到 GitHub。
3. 必须申请软著（审核已变严，材料合规性要在开发阶段就设计进去）。
4. 技术选型以 Python 为主，前端能薄则薄。

## 五、软著合规计划（开发阶段就要满足）

- **第 3 周前 GUI 必须能跑**（说明书必须带界面截图）。
- **冻结 v1.0 登记版本**：申请材料与 v1.0 绑定，之后继续迭代不受影响。
- 源代码只提交**自己写的核心代码**（本项目核心是 Python，天然合规），写注释。
- 说明书截图必须与软件名称、实际功能一一对应。
- 第 4 周产出软著材料包：源程序整理（前后各 30 页/每页 50 行）、带截图的说明书、申请表信息清单。
- 常见驳回雷区（需全程规避）：框架/脚手架代码充数、代码与文档功能不对应、缺截图、名称不规范、版本号与日期矛盾。

## 六、AI 助手（指导教师）工作规范

1. 采用 grill-me 模式：**一次只问一个问题**，每个问题给出推荐答案及理由，与用户对齐后再进入下一问。
2. 每项决策确认后，**立即更新本文件**的「已确认决策」和「待决策问题树」。
3. 涉及政策、软著等时效性信息时，用 web_search 核实，不凭记忆断言。
4. 指导风格：保姆级、可执行、给具体到文件/命令的步骤；**任务卡队列制（不打卡、不催进度，尊重用户弹性时间）**；用户编码需较多时间投入（自评），任务卡应切得更细、提示更足；鼓励用户亲手写代码，AI 负责设计、审查和答疑，不让用户沦为旁观者。
5. **git 完全由用户自管**：AI 不代为执行、不检查、不催促用户的 git 操作（用户明确划定的边界）。
6. 阶段产出的设计文档（如 PRD、架构图、排期表）也写入 `E:\项目` 下的文件，保持仓库可追溯。
7. **发修复/任务指令前必须先读用户当前代码**（用户明确要求，曾发生引用不存在字段 `ctx.search_cfg_max` 的失误）；涉及 ctx/对象字段时必须基于实际代码，禁止凭空造变量；修复建议给出精确行号锚点。

## 七、待决策问题树（按依赖顺序，逐个解决）

- [x] **Q4 功能边界**：v1.0 到底做什么、不做什么（砍字诀）。✅ 已确认，含 FDV 图表范式、LLM 双渠道、检索可插拔（Q4a/Q4b/Q4c）。
- [x] **Q5 报告形态**：输出什么样式的报告（Markdown/HTML/PDF？图文混排方式？图表类型？）。✅ 已确认：Markdown→HTML→打印PDF，中文报告。
- [x] **Q6 数据/检索来源**：已定"联网检索+可插拔"。✅ 已确认：Tavily 默认+DDGS 兜底、trafilatura 抓正文+降级链、检索策略、额度缓存；Q6a 插件注册机制（providers/ 自动发现，LLM/检索器/抓取器三扩展点共用）。
- [x] **Q7 LLM 选型**：已定"本地/在线双渠道"。✅ 已确认：OpenAI 兼容统一层；本地 qwen3:8b（8GB 显存）；在线默认 DeepSeek；Q7a：v1.0 内置双 Verifier，VisionVerifier 推荐 GLM-5.3-Flash（= OpenRouter ox-alpha）。
- [x] **Q8 Agent 框架**：LangChain / LangGraph / 手写 ReAct 循环？✅ 已确认：手写最小内核（Planner→JSON动作循环→Synthesizer），接口化以便日后迁移 LangGraph。
- [x] **Q9 前端形态**：Streamlit / Gradio / FastAPI+Vue？✅ 已确认：Streamlit。
- [x] **Q10 质量与评测**：✅ 已确认：报告自检器 + 引用真实性校验 + 回归样例集；不做自动评分框架。
- [x] **Q11 软著名称与版本策略**：✅ 已确认：「智绘研报图文报告智能生成系统 V1.0」+ 冻结策略（tag v1.0 → 材料从 tag 生成 → 继续迭代）。
- [x] **Q12 排期表**：✅ 已确认：28 天排期 + 波动预案，固化于 `docs/PLAN.md`。
- [x] **Q13 与科研的衔接**：✅ 已确认：模块边界↔论文组件映射，固化于 `docs/ARCHITECTURE.md` §6。
- [x] **Q14 部署/运行环境**：✅ 已确认：本地源码运行、不打包，固化于 `docs/ARCHITECTURE.md` §7。

## 八、开工指引（当前阶段）

设计已全部冻结（Q1~Q14）。**当前阶段：D12~D13 进行中（报告合成 Synthesizer + M2 里程碑）**。

- ✅ D2~D3 验收通过：smoke 三用例全绿（chat / JSON / 剥壳容错）；必改项全部落实（rfind、f 前缀、四个 __init__.py、importlib.import_module、FileNotFoundError、fail-fast、logging）。遗留小项（不卡验收）：chat 返回 None 兜底、报错信息带环境变量名、smoke prompt 双引号 JSON。
- ✅ D4~D5 **验收通过**：Tavily 真实调用 1.17s + 二次缓存命中；缓存键已纳入 `provider.name`（验证方式：DDGS 同 query 不再偷缓存、真出网并超时——超时为已知国内网络问题，Tavily 绝对主力，DDGS 仅兜底）。待确认：smoke 打印标题在用户终端是否乱码（疑为粘贴丢失）。当前进行 **D6：Fetcher 三级降级链**（trafilatura→bs4→空串，任何异常不外抛、logging.warning 记录降级）+ smoke_fetch（真实 URL 2 个 + 不可达 URL 1 个）。D6 后为 M1：search→fetch→证据 JSON 落盘的 CLI 串联 + 里程碑复盘。
- ✅ D6 **验收通过**：fetch_page 三级降级完整（空①`!=200` ②`len(text)>100` 均答对）、smoke 三用例通过（可达×2 + 不可达优雅降级不崩）。概念回答正确（保护 Agent 管线不中断）+ 补充"空串+日志=信号机制"细节。小改进项（不卡验收）：logger 惰性格式化（%s 而非 f-string）、smoke 打印正文预览。
- ✅ M1 **验收通过**（第 1 周完成）：主题"大模型推理加速"→ 14 条证据落盘（11 抓取成功 + 3 摘要兜底，平均 6042 字），降级链全程无崩溃；期间排雷：LLM 直构绕过 builder（应走 registry）、SearchProvider 直构抽象类、缺 discover/缓存、output_dir 传 str 应为 Path（雷#3）。**复盘结论**：①类型纪律是本周主要报错源（dict[] vs obj.attr、str vs Path、参数顺序）→ 对策：写前读签名、CLI 卡附签名清单 ②组装层比业务层易错 → CLI 卡给签名清单 ③新概念卡维持概念课+填空骨架。
- ✅ D8 **验收通过**：plan_outline 输出 6 章逻辑连贯提纲（硬件/压缩/算法/分布式/案例/未来），截断/兜底/字段过滤正确，smoke 组装规范。建议项（不卡验收）：LLM 章节缺 keywords 时 `OutlineSection(**s)` 抛 TypeError 会整提纲兜底 → 建议 `{**s, "keywords": s.get("keywords", [])}`。
- ✅ D9~D11 **验收通过**（Agent 内核）：单章循环 steps=2（一次 search → write_section），正文带 [1]~[4] 引用、内容确来自证据库（含具体数字）、降级链无崩溃；排雷：AgentContext 漏传 state（教训：必填字段不给默认值，错误要在源头爆炸）。**新决策**：引用编号按章节内证据编号管理，参考来源清单按章列出（全局编号留 v2.0）。
- ✅ M2 **验收通过（D13b 收官）**：6 章 / 正文各章 398~582 字（≥400 规则生效）/ 总 6403 字 / 30 证据 / 385.5s 全程零崩溃；叠标题/[nX]/脏标题问题修复生效，用户确认"格式好多了"。用户新诉求（已工程化立项）：①抓取成功率低 → 根因 = zhihu/华为 403 反爬 + Google/YouTube/Medium 国内不可达（非代码缺陷），且 fetch 无缓存致重跑重复踩坑 → D13c 加 FetchCache（只缓存成功内容）②引用权威性 → D14 接 arXiv API（免费无 key REST+Atom XML），作为 extra_providers 附加检索源（插件机制落地，arXiv 结果标记置前）；配套：PLANNER_PROMPT 要求 keywords 附英文翻译、AGENT_SYSTEM_PROMPT 加权威来源优先级规则。W2 完成；之后进 W3（FDV 图表 + HTML 渲染 + 自检器 + GUI 红线）。
- ✅ **D13c/D14 验收通过**：FetchCache 落地（单元验证 4177 字抓取→命中秒回；INFO 日志全景可见）；**用户自主 pivot：arXiv 需科学上网不可用 → 新增 OpenAlex provider 为主力学术源**（api.openalex.org 国内可达、免费无 key、处理 abstract_inverted_index 倒排还原、按 cited_by_count 排序、DOI 优先），arxiv_search.py 保留备用；extra_providers=["openalex"] config 驱动。排雷 2 处：search_tool 的 evs.append 缩进错位致学术证据被静默丢弃（else 分支内）、results[:5] 切片饿死主检索器（学术源占满 5 个名额）→ 已修。**报告实测**：仅 1 篇论文进报告（中文查询词在 OpenAlex 无结果）。
- ✅ **D14b 验收通过 / W2 收官**：keywords_en 生效（报告引用 6 篇权威论文：Lottery Ticket、剪枝系列、Lightweight DL 综述）；write_section 质量闸门排雷完成——闸门破坏"write_section 必然保存"的跨层假设致第 4 章 0 字 → core.py 改为"保存成功才终局、被拒回灌重试"（教训：层间成功/失败信号必须显式传递）。复测全绿：5 章 505/495/501/442/577 字、总 5784 字、50 证据、236s（缓存积累 604→236）。**W2 完整链路**：规划(中英) → 检索(web+学术 OpenAlex) → 抓取(降级+FetchCache) → 动作循环(上限/熔断/闸门/零字修复) → 合成 → 报告。
- ✅ **D15/D16/D17 验收通过**：FDV 三件套落地（render_chart + draw_chart 工具 + TextVerifier，含 verify_mode 拼写与 err 详情两处修复）；md→HTML 渲染完成（CSS 中文模板 + 图片 base64 内嵌单文件自包含 + 缺失图容错），浏览器目测 OK；排障记录：webbrowser file:// 被 360 劫持 → 改用 os.startfile（Windows 原生文件关联）。**当前 D18 进行中**：报告自检器 src/report/checker.py——CheckItem(level ok/warn/error) + run_checks(state)：①引用越界检查（正文 [n] ≤ 本section 证据数，复用 parse_citations）②图表一致性（state.chart 记录 vs 正文是否引用、文件是否存在、verified 标记）③结构完整性（章节数/正文长度/占位检测）④总字数 ≥ min_words；format_check_report 输出 ✅/⚠️/❌ 清单；m2_report 收尾打印；自检器=未来科研评测指标雏形。
- 🔧 已排查：①`.env.example` 模板曾误拼 `TAVIY_API_KEY`（缺 L）→ 已修复为 `TAVILY_API_KEY`，用户需同步改 `.env` 行名；②DDGS 底层抓 Yahoo，国内直连易超时（已知网络问题），Tavily 为绝对主力，DDGS 仅兜底；可选方向：代理参数或自写 bing 检索器插件。

- ✅ D1 基本完成：conda 环境 **ZHYB**（用户自命名，Python 3.11）、依赖装齐、`.env` 已填、qwen3:8b 已拉取。
- ⚠️ D1 遗留：git 因目录归属（Administrator 所有）报 dubious ownership，需用户在自己终端执行
  `git config --global --add safe.directory 'E:/项目/deepresearch-report-agent'` 后完成首次 commit。
- 执行模式（用户偏好，已确认）：**任务卡队列制**——按 `docs/PLAN.md` 顺序逐卡推进，有空即做、做完发验收，不设每日打卡；软著提交目标 ≤ 开工后 6 周，超 8 周 AI 主动提醒评估砍需求。
- 协作流程：发任务卡（文件清单+接口约定+验收标准）→ 用户写代码 → 贴代码 AI review → 验收通过发下一卡；每里程碑复盘；关键决策写入本文件。

## 九、更新日志

- 2026-XX-XX：创建本文件，固化 Q1~Q3 决策与问题树。
- 同日：确认 Q4 功能边界及 Q4a（FDV 范式）/Q4b（LLM 双渠道）/Q4c（检索可插拔）。
- 同日：确认 Q5 报告形态（Markdown→HTML→打印PDF，中文）。
- 同日：确认 Q6 检索方案与 Q6a 插件注册机制。
- 同日：确认 Q7 LLM 选型与 Q7a（双 Verifier + GLM-5.3-Flash 视觉校验）。
- 同日：确认 Q8 手写 Agent 内核（不用 LangChain/LangGraph）。
- 同日：确认 Q9 前端形态（Streamlit）。
- 同日：确认 Q10 质量自检方案（自检器+引用校验+回归样例集）。
- 同日：确认 Q11 名称「智绘研报图文报告智能生成系统 V1.0」与冻结策略。
- 同日：grill-me 收尾——确认 Q12 排期、Q13 科研衔接、Q14 运行环境；项目迁移至子目录 `deepresearch-report-agent/`，建骨架（.gitignore/.env.example/config.yaml/requirements.txt/README + docs/PRD.md + docs/ARCHITECTURE.md + docs/PLAN.md），设计冻结，待 D1 开工。
- D1：环境地基基本完成（conda 环境 ZHYB、依赖、.env、qwen3:8b）；确认"任务卡队列制"执行模式；git 归属问题待用户修复后补 commit；进入 D2~D3（LLM 提供者层）。
- D2~D3：LLM 提供者层代码已交并完成首轮 review（3 必改 + 若干建议项）；确立"git 完全由用户自管"边界；任务卡后续将更细粒度。
- D2~D3 验收通过（smoke 三用例全绿）；发放 D4~D5 检索层任务卡（拆为 D4 接口+缓存 / D5 双检索器联调两小卡）。
- D4~D5 联调验收：Tavily+缓存链路通过；发现缓存键未区分 provider 的隐蔽 bug（DDGS 假绿）→ 用户修复（缓存键加入 provider.name）后复测通过：DDGS 同 query 真出网超时（证明修复生效，超时为已知国内网络问题）；待确认终端标题显示；D6 进行中。
- D6 教学式推进：用户反馈 Fetcher 难度大（首次接触 HTML 解析/第三方库/网络异常）→ 已发放"概念课+填空骨架"教学版任务卡（函数主体基本给全，留 2 个小填空；smoke_fetch.py 由用户独立完成）；工作规范补充：新概念任务卡采用教学式（先讲概念→给骨架→留填空→独立验收脚本）。
- D6 验收通过（降级链完整、smoke 三用例通过）；发放 M1 里程碑卡（state.py + pipeline.py + m1_pipeline.py，LLM 改写查询词 + 检索 + 抓取 + 证据落盘串联）；M1 后里程碑复盘。
- M1 验收通过（14 条证据落盘，11 成功+3 兜底）；完成里程碑复盘（类型纪律/组装层易错/教学式卡维持）；发放 D8 Planner 卡；D8 后为 core.py 动作循环。
- D8 验收通过（6 章提纲，建议项：keywords 缺失防护）；发放 D9~D11 Agent 内核卡（RunState + tools.py + core.py 动作循环）；之后为 D12 报告合成与 M2。
