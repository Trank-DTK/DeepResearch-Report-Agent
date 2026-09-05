import sys
from src.utils.config import get_search_config
from src.providers.registry import discover,get as get_registry



def main():
  topic = sys.argv[1] if len(sys.argv) > 1 else "大模型推理加速"
  print(f"开始收集证据，主题为：{topic}")
  discover()  #发现并注册所有providers
  search_cfg = get_search_config()
  p = get_registry("search","openalex")({})
  res = p.search("large language model inference acceleration")
  for r in res[:5]:
    print(f"url:{r.url}")
    print(f"title:{r.title}")
    print(f"snippet:{r.snippet[:80]}")


  print("收集证据完成")


if __name__ == "__main__":
  main()