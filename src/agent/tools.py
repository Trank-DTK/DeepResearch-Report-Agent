import logging
from pathlib import Path
from datetime import datetime
from src.retrieval.cache import search_multi,cached_search
from src.retrieval.fetch import cached_fetch
from .state import Evidence

logger = logging.getLogger(__name__)

TOOLS:dict[str,callable] = {}

def register_tool(name:str):
  """工具注册装饰器"""
  def decorator(func):
    TOOLS[name] = func
    return func
  return decorator

@register_tool("search")
def search_tool(args:dict,ctx) -> str:
  """搜索+抓取工具 证据保存到ctx.evidence_by_section[当前章]，返回给LLM的文本每条证据都带有[编号]前缀"""
  query = args["query"]
  try:
    section = next((s for s in ctx.state.outline if s.id == ctx.state.current_section_id),None)
    kw_en = getattr(section,"keywords_en",None) or []
    query_en = " ".join(kw_en) if kw_en else query
    results = []
    for p in ctx.extra_providers:
      results += cached_search(p,ctx.cache,query_en,5)
    results += cached_search(ctx.search_provider,ctx.cache,query)
  except Exception as e:
    logger.warning("搜索工具异常: %s",e)
    return f"搜索失败：{e}。你可以换一个查询词重试，或直接write_section基于现有证据写作"
  evs = []
  for r in results: #最多10条
    if r.provider in ("arxiv","openalex"):
      content = r.snippet
      degraded = False
    else:
      content = cached_fetch(r.url,ctx.fetch_cache,timeout=ctx.fetcher_cfg["timeout"],user_agent=ctx.fetcher_cfg["user_agent"])
      degraded = False
      if not content:
        content = r.snippet
        degraded = True
    evs.append(Evidence(url=r.url,title=r.title,content=content,source_query=query,
                          section_id=str(ctx.state.current_section_id),provider=r.provider,
                          fetched_at=datetime.now().isoformat(),degraded=degraded))
  #去重并入库 
  key = ctx.state.current_section_id
  existing = ctx.state.evidence_by_section.setdefault(key,[])
  seen = {e.url for e in existing}
  for e in evs:
    if e.url not in seen:
      existing.append(e)
      seen.add(e.url)
  #返回给LLM摘要，每条带编号+前300字
  lines = []
  for i,e in enumerate(existing,1):
    lines.append(f"[{i}]{e.title}|{e.url}\n{e.content[:300]}")
  return f"本章已有{len(existing)}条证据:\n" + "\n".join(lines)

@register_tool("write_section")
def write_section_tool(args:dict,ctx) -> str:
  markdown = args.get("markdown","").strip()
  if len(markdown) < 300:
    return f"正文过短({len(markdown)}字),请扩写到至少300字（包含更多证据细节与引用）后重新write_section"
  if not markdown:
    return "错误:markdown为空，请重新输出"
  ctx.state.section_markdown[ctx.state.current_section_id] = markdown
  return "章节已保存"

@register_tool("finalize")
def finalize_tool(args:dict,ctx) -> str:
  return "本章结束"