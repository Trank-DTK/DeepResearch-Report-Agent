import logging
from ddgs import DDGS
from src.retrieval.search import SearchProvider,SearchResult
from src.providers.registry import register

logger = logging.getLogger(__name__)

@register("search","ddgs")
class DDGSSearchProvider(SearchProvider):
  name:str = "ddgs"

  def __init__(self,cfg:dict|None = None):
    pass

  def search(self, query, max_results = 5) -> list[SearchResult]:
    try:
      with DDGS() as d:
        return [SearchResult(url=r["href"],title=r["title"],snippet=r.get("body",""),provider="ddgs") for r in d.text(query,max_results=max_results)]
    except Exception as e:
      logger.warning("DDGS搜索失败 %s:%s ，返回空结果",query,e)
      return []