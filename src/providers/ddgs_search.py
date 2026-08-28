from ddgs import DDGS
from src.retrieval.search import SearchProvider,SearchResult
from src.providers.registry import register

@register("search","ddgs")
class DDGSSearchProvider(SearchProvider):
  def __init__(self,cfg:dict|None = None):
    pass

  def search(self, query, max_results = 5) -> list[SearchResult]:
    with DDGS() as d:
      return [SearchResult(url=r["href"],title=r["title"],snippet=r.get("body",""),provider="ddgs") for r in d.text(query,max_results=max_results)]
    