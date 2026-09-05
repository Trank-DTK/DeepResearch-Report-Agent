import sys
import time
from pathlib import Path
from src.agent.state import RunState
from src.agent.planner import plan_outline
from src.agent.core import AgentContext,run_section
from src.report.synthesizer import assemble_report,save_report
from src.retrieval.search import build_search_provider
from src.retrieval.cache import SearchCache
from src.utils.config import get_llm_config,get_fetcher_config,get_search_config,get_chart_config
from src.providers.registry import discover,get as get_registry
from src.retrieval.fetch import FetchCache
from src.report.render import render_report

import logging
logging.basicConfig(level=logging.INFO,format="%(levelname)s %(name)s:%(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)

def main():
  topic = sys.argv[1] if len(sys.argv) > 1 else "大模型推理加速"
  print(f"开始收集证据，主题为：{topic}")
  discover()  #发现并注册所有providers
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
    print(f"第{i}/{len(outline)}章完成，正文{len(md)}字")
  report = assemble_report(state,llm_client=llm_client)
  md_path = save_report(report,Path("data/outputs"),topic)
  html_path = md_path.with_suffix(".html")
  render_report(report,html_path)
  print(f"HTML报告:{html_path}")
  elapsed = time.time() - start
  print(f"章节数:{len(outline)}")
  print(f"总字数:{len(report)}")
  total_evs = sum(len(v) for v in state.evidence_by_section.values())
  print(f"总证据数:{total_evs}")
  print(f"总耗时:{elapsed:.1f}秒")

  
  
  print("收集证据完成")


if __name__ == "__main__":
  main()