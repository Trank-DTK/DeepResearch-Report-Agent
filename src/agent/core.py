import logging
from dataclasses import dataclass,field
from .tools import TOOLS

logger = logging.getLogger(__name__)

import json

#为了避免部分模型乱起名字
ACTION_ALIASES = {
    "web_search":"search","search_web":"search","search_tool":"search",
    "google":"search","retrieve":"search",
    "write":"write_section","write_section_tool":"write_section",
    "submit":"write_section","complete":"write_section","finish":"write_section",
    "plot":"draw_chart","chart":"draw_chart","draw":"draw_chart","create_chart":"draw_chart",
    "end":"finalize","done":"finalize","stop":"finalize",
}

def _normalize_action(raw) -> str:
  """不同模型的工具名变体归一化"""
  if isinstance(raw,dict):
    raw = raw.get("name") or raw.get("tool") or ""
  name = str(raw or "").strip().lower()
  if name in TOOLS:
    return name
  if name in ACTION_ALIASES:
    return ACTION_ALIASES[name]
  if name.endswith("_tool") and name[:-5] in TOOLS:
    return name[:-5]
  return name


AGENT_SYSTEM_PROMPT = """你是深度研究报告的章节撰写专家。当前章节的问题会给出。
你可以使用的工具：
1.search:参数{"query":"搜索查询词"}，搜索并抓取网页，证据会以[编号]列出
2.write_section:参数{"markdown":"章节正文"}，必须基于证据撰写，引用标[n]（n=证据编号）
3.finalize:参数{}，结束本章
4.draw_chart:参数{"chart_type":"bar|line|pie","title":"图标题","data":[{"label":"类别","value":数值}]},
图表数据必须来自本章证据中的真实数字（可含单位/年份），每章最多2张图表，成功后把返回的图片行插入正文。
每次只输出一个JSON：{"thought":"你的思考","action":"工具名","args":{...}}
引用规则（必须严格遵守）
1.正文引用只允许 [1] 这样的数字编号，禁止 “证据1”、“[n1]” 等其他写法
2.每个具体事实后必须紧跟引用
其他规则（必须严格遵守）
1.正文开头禁止重复章节标题或研究主题，直接写内容
2.正文内的小节标题用####，禁止使用#或##
3.write_section前确保检索过足够证据，正文不少于450字，且按内容逻辑尽量分小节
（证据充足时3~5小节，不足时至少2小节）每节用####标题
4.优先引用权威来源（如学术论文、官方文档等）
5.如果本章证据含2个以上可对比数值（性能/占比/趋势），应先用draw_chart配图并在正文引用
6.action字段只能是:search / write_section / draw_chart / finalize 必须完全一致，禁止自创名称。参数固定放在args字段
"""

@dataclass
class AgentContext:
  llm_client: object
  search_provider: object
  cache: object
  fetcher_cfg: dict
  fetch_cache:object
  state: object
  chart_cfg:dict
  extra_providers:list = field(default_factory=list)

def run_section(ctx:AgentContext,section)->str:
  """跑完一个章节，返回该章节的Markdown正文"""
  ctx.state.current_section_id = section.id
  ctx.state.steps_taken = 0

  messages = [
    {"role":"system","content":AGENT_SYSTEM_PROMPT},
    {"role":"user","content":f"本章节问题:{section.question}\n检索关键词：{'、'.join(section.keywords)}"},
  ]
  
  max_steps = 8
  unknown_count = 0
  for step in range(max_steps):
    ctx.state.steps_taken += 1
    try:
      act = ctx.llm_client.chat_json(messages)
    except Exception as e:
      logger.error("第%d章LLM调用失败：%s，本章终止",section.id,e)
      return ctx.state.section_markdown.get(section.id,"") or "[本章生成失败：LLM服务异常]"
    
    raw_action = act.get("action")
    action = _normalize_action(raw_action)
    args = act.get("args") or act.get("arguments") or act.get("parameters") or {}
    if not isinstance(args,dict):
      args = {}
    if action not in TOOLS:
      unknown_count += 1
      logger.warning("未知动作%r (原始action=%r,args=%r)",action,raw_action,args)
      if unknown_count >= 3:
        logger.warning("连续%d次未知动作，结束本章",unknown_count)
        break
      messages.append({"role":"assistant","content":json.dumps(act,ensure_ascii=False)})
      messages.append({"role":"user","content":"你的action不合法。action只能取以下之一（必须完全一致）："
        "search / write_section / draw_chart / finalize。请重新只输出一个JSON"})
      continue
    unknown_count = 0

    try:
      res = TOOLS[action](args,ctx) 
    except Exception as e:
      logger.warning("工具 %s 执行异常:%s",action,e)
      messages.append({"role":"user","content":f"工具执行出错：{e}。请修正参数或换一种做法后重试"})
      continue

    if action == "write_section":
      saved = ctx.state.section_markdown.get(section.id,"")
      if saved:
        logger.info("第%d章完成，写入%d字",section.id,len(saved))
        return saved
      messages.append({"role":"assistant","content":f"我选择执行:write_section，因为:{act.get('thought','')}"})
      messages.append({"role":"user", "content": f"工具结果:\n{res}"})
      continue

    #其他动作：把本轮决策与工具结果写回对话历史
    messages.append({"role":"assistant","content":f"我选择执行:{action},因为:{act.get('thought','')}"})
    messages.append({"role":"user","content":f"工具结果:\n{res}"})
  
  if not ctx.state.section_markdown.get(section.id):
    evs = ctx.state.evidence_by_section.get(section.id,[])
    digest = "\n".join(f"[{i}]{e.title}:{e.content[:400]}" for i,e in enumerate(evs,1))
    try:
      body = ctx.llm_client.chat([
        {"role":"system","content":"你是研究报告撰写者。只输出章节正文的Markdown，不要输出JSON，不要解释。"},
        {"role":"user","content":f"章节问题:{section.question}\n"
                                f"可用证据:\n{digest[:4000]}\n\n"
                                f"请撰写本章正文，不少于350字，分2~3个 #### 小节，事实后用 [编号] 标注引用来源。"},
      ]) or ""
      if len(body.strip()) >= 150:
        ctx.state.section_markdown[section.id] = body.strip()
        logger.info("第%d章保底成稿成功，写入%d字",section.id,len(body.strip()))
    except Exception as e:
      logger.warning("第%d章保底成稿失败：%s",section.id,e)

  logger.warning("第%d章达到步数上线或异常结束",section.id)
  return ctx.state.section_markdown.get(section.id,"") or "[本章生成失败：证据不足或超出循环限制]"