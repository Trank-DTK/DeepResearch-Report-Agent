import logging
from dataclasses import dataclass,field
from .tools import TOOLS

logger = logging.getLogger(__name__)

AGENT_SYSTEM_PROMPT = """你是深度研究报告的章节撰写专家。当前章节的问题会给出。
你可以使用的工具：
1.search:参数{"query":"搜索查询词"}，搜索并抓取网页，证据会以[编号]列出
2.write_section:参数{"markdown":"章节正文"}，必须基于证据撰写，引用标[n]（n=证据编号）
3.finalize: 参数{}，结束本章
每次只输出一个JSON：{"thought":"你的思考","action":"工具名","args":{...}}"""

@dataclass
class AgentContext:
  llm_client: object
  search_provider: object
  cache: object
  fetcher_cfg: dict
  state: object

def run_section(ctx:AgentContext,section)->str:
  """跑完一个章节，返回该章节的Markdown正文"""
  ctx.state.current_section_id = section.id
  ctx.state.steps_taken = 0

  messages = [
    {"role":"system","content":AGENT_SYSTEM_PROMPT},
    {"role":"user","content":f"本章节问题:{section.question}\n检索关键词：{'、'.join(section.keywords)}"},
  ]
  
  max_steps = 8
  for step in range(max_steps):
    ctx.state.steps_taken += 1
    act = ctx.llm_client.chat_json(messages)
    action = act.get("action")
    args = act.get("args",{}) or {}
    if action not in TOOLS:
      logger.warning("未知动作'%s'，结束本章",action)
      break
    if action == "write_section":
      #如果是写章节，直接调用工具并结束
      res = TOOLS[action](args,ctx)
      logger.info("第%d章完成，写入%d字",section.id,len(ctx.state.section_markdown.get(section.id,"")))
      return ctx.state.section_markdown.get(section.id,"")
    
    #其他动作，调用工具并把结果作为下一轮的用户输入
    res = TOOLS[action](args,ctx)
    messages.append({"role":"assistant","content":f"我选择执行:{action},因为:{act.get('thought','')}"})
    messages.append({"role":"user","content":f"工具结果:\n{res}"})
  
  logger.warning("第%d章达到步数上线或异常结束",section.id)
  return ctx.state.section_markdown.get(section.id,"") or "[本章生成失败：证据不足或超出循环限制]"
      