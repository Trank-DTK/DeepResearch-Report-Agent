import logging
from dataclasses import dataclass,field
from pathlib import Path
from datetime import datetime
from src.retrieval.cache import cached_search
from src.retrieval.fetch import fetch_page
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
  results = cached_search(ctx.search_provider,ctx.cache,query)
  evs = []
  for r in results[:5]: #只取前5条
    content = fetch_page(r.url,timeout=ctx.fetcher_cfg["timeout"],user_agent=ctx.fetcher_cfg["user_agent"])
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
  markdown = args.get("markdown","")
  if not markdown:
    return "错误:markdown为空，请重新输出"
  ctx.state.section_markdown[ctx.state.current_section_id] = markdown
  return "章节已保存"

@register_tool("finalize")
def finalize_tool(args:dict,ctx) -> str:
  return "本章结束"