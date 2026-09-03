import httpx
import os
import logging
from src.retrieval.search import SearchProvider,SearchResult
from src.providers.registry import register

logger = logging.getLogger(__name__)


@register("search","tavily")
class TavilySearchProvider(SearchProvider):
  name:str = "tavily"

  def __init__(self,cfg:dict):
    env_name = cfg.get("tavily_api_key_env","")
    api_key = os.getenv(env_name) if env_name else None
    if not api_key:
      raise ValueError(f"环境变量{env_name}未设置，请在.env文件中配置")
    self.api_key = api_key
    self.timeout = cfg.get("timeout",15.0)

  def search(self, query, max_results = 5) -> list[SearchResult]:
    try:
      res = httpx.post(
        "https://api.tavily.com/search",
        json={
          "api_key":self.api_key,"query":query,"max_results":max_results,"include_answer":False
        },
        timeout = self.timeout
      )
      res.raise_for_status()
    except httpx.HTTPError as e:
      logger.warning("Tavily搜索失败 %s:%s ，返回空结果",query,e)
      return []
    return [SearchResult(url=r["url"],title=r["title"],snippet=r.get("content",""),provider="tavily") for r in res.json().get("results",[])]
  
    