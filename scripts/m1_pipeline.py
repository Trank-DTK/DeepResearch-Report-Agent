import sys
from pathlib import Path
from src.agent.pipeline import collect_evidence
from src.retrieval.search import build_search_provider
from src.retrieval.cache import SearchCache
from src.utils.config import get_llm_config,get_fetcher_config,get_search_config
from src.providers.registry import discover,get as get_registry



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
  evidence_list = collect_evidence(topic,llm_client,search_provider,cache,fetcher_cfg,output_dir=Path("data/evidence"))
  print(f"收集到{len(evidence_list)}条证据")
  print("收集证据完成")


if __name__ == "__main__":
  main()