import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

PLANNER_PROMPT = """你是研究报告规划师，把用户的研究主题拆解为3到6个逻辑连贯的章节，
每章是一个需要联网搜索才能回答的子问题，只输出JSON:
{"sections":[{"id":1,"title":"章节标题","question":"该章要回答的子问题","keywords":["关键词1","关键词2"]}]}"""


@dataclass
class OutlineSection:
  id: int
  title: str
  question: str
  keywords: list[str]

def plan_outline(llm_client,topic:str,min_sections:int=3,max_sections:int=6)->list[OutlineSection]:
  """规划研究报告章节大纲规划"""
  try:
    result = llm_client.chat_json([{"role":"system","content":PLANNER_PROMPT},{"role":"user","content":f"研究主题:{topic}"}])
    raw = result.get("sections",[])
    raw = raw[:max_sections]  #限制最大章节数
    if len(raw) < min_sections:
      logger.warning("章节数%s<%s，按最小章节处理",len(raw),min_sections)
    return [OutlineSection(**{**s,"keywords":s.get("keywords",[])}) for s in raw if s.get("title") and s.get("question")]  #为了防止缺少keywords字段
  except Exception as e:
    logger.warning("章节规划失败：%s，使用兜底提纲",e)
    return [OutlineSection(id=1,title=topic,question=topic,keywords=[topic])]



