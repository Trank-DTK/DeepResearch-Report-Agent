import logging
import httpx
from src.retrieval.search import SearchProvider, SearchResult
from src.providers.registry import register

logger = logging.getLogger(__name__)

@register("search","openalex")
class OpenAlexSearchProvider(SearchProvider):
    name = "openalex"

    def __init__(self, cfg:dict | None=None):
        self.timeout = (cfg or {}).get("timeout",20.0)

    @staticmethod
    def _reconstruct_abstract(inverted:dict | None) -> str:
        """OpenAlex的摘要是倒排索引，要还原成句子。"""
        if not inverted:
            return ""
        pos = {}
        for word, idxs in inverted.items():
            for i in idxs:
                pos[i] = word
        return " ".join(pos[i] for i in sorted(pos))

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        try:
            resp = httpx.get(
                "https://api.openalex.org/works",
                params={"filter":f"title_and_abstract.search:{query}","per-page":max_results,"sort":"cited_by_count:desc"},
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.warning("OpenAlex 检索失败 %s: %s", query, e)
            return []

        out = []
        for w in resp.json().get("results", []):
            title = w.get("display_name") or "无标题"
            abstract = self._reconstruct_abstract(w.get("abstract_inverted_index"))
            url = w.get("doi") or w.get("id") or ""      #优先DOI链接（国内可达）
            out.append(SearchResult(
                url=url,
                title=f"[论文] {title}",
                snippet=f"(被引{w.get('cited_by_count',0)}次，{w.get('publication_year','')}年) {abstract[:500]}",
                provider="openalex",
            ))
        return out