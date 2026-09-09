import logging
import time
from pathlib import Path
from src.agent.state import RunState
from src.agent.planner import plan_outline
from src.agent.core import AgentContext, run_section
from src.report.synthesizer import assemble_report, save_report,consolidate_reference
from src.report.render import render_report
from src.report.checker import run_checks, format_check_report
from src.report.auto_chart import auto_illustrate
from src.retrieval.search import build_search_provider
from src.retrieval.cache import SearchCache
from src.retrieval.fetch import FetchCache
from src.utils.config import get_llm_config, get_fetcher_config, get_search_config, get_chart_config
from src.providers.registry import discover, get as get_registry


logger = logging.getLogger(__name__)

def run_full_report(topic:str) -> dict:
  """跑完整报告流水线，返回结果字典"""
  discover()
  llm_cfg = get_llm_config()
  fetcher_cfg = get_fetcher_config()
  search_cfg = get_search_config()
  builder = get_registry("llm",llm_cfg["provider"])
  if not builder:
    raise ValueError(f"未找到llm构建器: {llm_cfg['provider']}")
  llm_client = builder(llm_cfg)
  search_provider = build_search_provider(search_cfg)
  cache = SearchCache(Path(search_cfg["cache_dir"]))
  fetch_cache = FetchCache(Path("data/cache/fetch"))
  outline = plan_outline(llm_client,topic)
  state = RunState(topic=topic,outline=outline)
  chart_cfg = get_chart_config()
  extra_providers = [get_registry("search",name)(search_cfg) for name in search_cfg.get("extra_providers",[]) if get_registry("search",name)]
  ctx = AgentContext(
    llm_client=llm_client,
    search_provider=search_provider,
    cache=cache,
    fetcher_cfg=fetcher_cfg,
    fetch_cache=fetch_cache,
    state=state,
    chart_cfg=chart_cfg,
    extra_providers=extra_providers
  )
  start = time.time()
  for i,section in enumerate(outline,1):
    md = run_section(ctx,section)
    logger.info(f"第{i}/{len(outline)}章完成，正文{len(md)}字")
  auto_made = auto_illustrate(state,llm_client,chart_cfg)
  logger.info("自动配图完成，共生成%d张",auto_made)
  consolidate_reference(state)
  report = assemble_report(state,llm_client=llm_client)
  md_path = save_report(report,Path("data/outputs"),topic)
  html_path = md_path.with_suffix(".html")
  checks = run_checks(state,min_words=2000)
  render_report(report,html_path)
  logger.info(f"HTML报告:{html_path}")
  elapsed = time.time() - start
  logger.info(f"章节数:{len(outline)}")
  logger.info(f"总字数:{len(report)}")
  total_evs = sum(len(v) for v in state.evidence_by_section.values())
  logger.info(f"总证据数:{total_evs}")
  logger.info(f"总耗时:{elapsed:.1f}秒")
  return {
    "topic": topic,
    "num_sections":len(outline),
    "md_path": md_path,
    "html_path": html_path,
    "checks": checks,
    "report": report,
    "elapsed": elapsed,
    "total_evidence": total_evs,
  }
