import logging
from pathlib import Path
from datetime import datetime
from src.retrieval.cache import search_multi,cached_search
from src.retrieval.fetch import cached_fetch
from .state import Evidence
from src.report.chart import render_chart
from src.report.verify import verify_chart_text

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


@register_tool("draw_chart")
def draw_chart_tool(args:dict,ctx) -> str:
  """画图+检验"""
  chart_type = args.get("chart_type","")
  title = str(args.get("title","")).strip() or "未命名图表"
  data = args.get("data") or []
  sid = ctx.state.current_section_id

  cur = ctx.state.chart.get(sid,[])
  if len(cur) >= 2:
    return "本章已有2张图，达到上限。请在正文中引用已有图表，不要再draw_chart"

  n = len(cur) + 1
  out_path = Path(ctx.chart_cfg["output_dir"]) / f"s{sid}_f{n}.png"
  err = render_chart(chart_type,title,data,out_path)
  if err:
    return f"绘图失败:{err}。请修正data后重试draw_chart"
  verdict = {"consistent":True,"issues":[],"suggestion":""}
  if ctx.chart_cfg.get("verify_mode","text") == "text" and ctx.llm_client:
    verdict = verify_chart_text(ctx.llm_client,chart_type,title,data)
  ctx.state.chart.setdefault(sid,[]).append(
    {"path":str(out_path),"caption":title,"chart_type":chart_type,"verified":verdict["consistent"]}
  )
  if not verdict["consistent"]:
    issues = ";".join(verdict.get("issues",[])) or verdict.get("suggestion","数据存疑")
    return f"图已生成，但校验未通过：{issues}。请核对证据中的真实数值后重新draw_chart，或直接write_section"
  return (f"图表已生成并通过校验，请把这一行插入正文合适位置:\n"
          f"![{title}]({out_path.as_posix()})")



