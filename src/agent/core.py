import logging
from dataclasses import dataclass,field
from .tools import TOOLS

logger = logging.getLogger(__name__)

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
3.正文开头禁止重复章节标题或研究主题，直接写内容
4.正文内的小节标题用####，禁止使用#或##
5.write_section前确保检索过足够证据，正文不少于400字
6.优先引用权威来源（如学术论文、官方文档等）
7.如果本章证据含2个以上可对比数值（性能/占比/趋势），应先用draw_chart配图并在正文引用"""

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
  for step in range(max_steps):
    ctx.state.steps_taken += 1
    try:
      act = ctx.llm_client.chat_json(messages)
    except Exception as e:
      logger.error("第%d章LLM调用失败：%s，本章终止",section.id,e)
      return ctx.state.section_markdown.get(section.id,"") or "[本章生成失败：LLM服务异常]"
    action = act.get("action")
    args = act.get("args",{}) or {}
    if action not in TOOLS:
      logger.warning("未知动作'%s'，结束本章",action)
      break
    if action == "write_section":
      #如果是写章节，直接调用工具并结束
      res = TOOLS[action](args,ctx)
      saved = ctx.state.section_markdown.get(section.id,"")
      if saved:
        #保存成功
        logger.info("第%d章完成，写入%d字",section.id,len(saved))
        return saved
      messages.append({"role":"assistant","content":f"我选择执行:write_section，因为:{act.get('thought','')}"})
      messages.append({"role":"user", "content": f"工具结果:\n{res}"})
      continue
      
    
    #其他动作，调用工具并把结果作为下一轮的用户输入
    res = TOOLS[action](args,ctx)
    messages.append({"role":"assistant","content":f"我选择执行:{action},因为:{act.get('thought','')}"})
    messages.append({"role":"user","content":f"工具结果:\n{res}"})
  
  logger.warning("第%d章达到步数上线或异常结束",section.id)
  return ctx.state.section_markdown.get(section.id,"") or "[本章生成失败：证据不足或超出循环限制]"
      