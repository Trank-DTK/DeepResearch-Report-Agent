import logging
import httpx
import xml.etree.ElementTree as ET
from src.retrieval.search import SearchProvider,SearchResult
from src.providers.registry import register

logger = logging.getLogger(__name__)
NS = {"atom":"http://www.w3.org/2005/Atom"}

@register("search","arxiv")
class ArxivSearchProvider(SearchProvider):
  name = "arxiv"

  def __init__(self,cfg:dict | None = None):
    self.timeout = (cfg or {}).get("timeout",20.0)

  def search(self, query, max_results = 5) -> list[SearchResult]:
    try:
      res = httpx.get(
        "https://export.arxiv.org/api/query",
        params={"search_query":f"all:{query}","max_results":max_results},
        timeout=self.timeout
      )
      res.raise_for_status()
    except httpx.HTTPError as e:
      logger.warning("arXiv检索失败 %s:%s",query,e)
      return []
    
    try:
      root = ET.fromstring(res.text)
    except ET.ParseError as e:
      logger.warning("arXiv响应解析失败:%s",e)
      return []
    
    results = []
    for entry in root.findall("atom:entry",NS):
      title = " ".join(entry.findtext("atom:title",default="",namespaces=NS).split())
      url = entry.findtext("atom:id",default="",namespaces=NS).strip()
      summary = " ".join(entry.findtext("atom:summary",default="",namespaces=NS).split())[:400]
      results.append(SearchResult(url=url,title=f"[arXiv] {title}",snippet=summary,provider="arxiv"))
    return results
    






