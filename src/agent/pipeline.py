import logging
from pathlib import Path
from .state import Evidence,save_evidence
from src.retrieval.cache import cached_search
from src.retrieval.fetch import fetch_page
from datetime import datetime

logger = logging.getLogger(__name__)

REWRITE_PROMPT = """你是专业的查询改写助手，把用户的研究主题改写为2~3个独立的搜索查询词，只输出JSON
格式：{"queries":["查询词1","查询词2","查询词3"]}"""

def rewrite_queries(llm_client,topic:str) -> list[str]:
  """LLM改写查询词"""
  try:
    result = llm_client.chat_json([
      {"role":"system","content":REWRITE_PROMPT},
      {"role":"user","content":topic},
    ])
    queries = result.get("queries",[])
    if queries:
      logger.info("改写查询词:%s",queries)
      return queries
  except Exception as e:
    logger.warning("查询词改写失败：%s，使用兜底查询词",e)
  return [topic]


def collect_evidence(topic:str,llm_client,search_provider,cache,fetcher_cfg:dict,output_dir:Path) -> list[Evidence]:
  queries = rewrite_queries(llm_client,topic)
  evidence_list : list[Evidence] = []
  seen_urls :set[str] = set()
  for query in queries:
    results = cached_search(search_provider,cache,query)
    for r in results:
      if r.url in seen_urls:
        continue
      seen_urls.add(r.url)  #去掉重复的链接
      content = fetch_page(r.url,timeout=fetcher_cfg["timeout"],user_agent=fetcher_cfg["user_agent"])
      degraded = False
      if not content:
        content = r.snippet
        degraded = True
        logger.warning("抓取正文失败，使用摘要兜底: %s",r.url)
      
      evidence_list.append(Evidence(
        url=r.url,
        title=r.title,
        content=content,
        source_query=query,
        provider=r.provider,
        fetched_at=datetime.now().isoformat(),
        degraded=degraded
      ))
  
  path = save_evidence(evidence_list,output_dir,topic)
  logger.info("证据收集完成，共%d条，保存路径: %s",len(evidence_list),path)
  return evidence_list





