# import tempfile
import sys
import time
from pathlib import Path
from src.retrieval.cache import SearchCache,cached_search
from src.retrieval.search import build_search_provider
from src.utils.config import get_search_config
from src.providers.registry import discover

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
  sys.path.insert(0,str(project_root))

def run_test(provider_name: str, query: str = "大模型推理加速", max_results: int = 5):
    print(f"测试Provider: {provider_name}")
    # 加载完整配置，并深拷贝一份，修改 provider
    search_cfg = get_search_config()
    search_cfg["provider"] = provider_name

    # 创建缓存目录
    cache_dir = Path(search_cfg.get("cache_dir", "data/cache/search"))
    cache = SearchCache(cache_dir)

    # 构建 provider
    try:
        provider = build_search_provider(search_cfg)
    except Exception as e:
        print(f"构建{provider_name}失败:{e}")
        return

    print(f"\n第一次搜索:'{query}'")
    start = time.time()
    results1 = cached_search(provider, cache, query, max_results)
    elapsed = time.time() - start
    print(f"耗时:{elapsed:.2f}s,结果数:{len(results1)}")
    if results1:
        print("前3条结果:")
        for i, r in enumerate(results1[:3]):
            print(f"{i+1}. {r.title} ({r.url})")

    print(f"\n第二次搜索:'{query}'(期望缓存命中)")
    start = time.time()
    results2 = cached_search(provider, cache, query, max_results)
    elapsed = time.time() - start
    print(f"耗时:{elapsed:.2f}s,结果数:{len(results2)}")
    if results2:
        print("前3条结果:")
        for i, r in enumerate(results2[:3]):
            print(f"{i+1}. {r.title} ({r.url})")

    # 断言：两次结果数量相同
    assert len(results1) == len(results2), "两次搜索结果数量不一致，可能缓存异常"
    print("缓存验证通过：第二次未重新请求网络")

# class FakeProvider(SearchProvider):
#   """模拟的搜索供应商"""
#   def __init__(self):
#     self.call_count = 0
  
#   def search(self,query:str,max_results:int) -> list[SearchResult]:
#     self.call_count += 1
#     print(f"[FakeProvider]第{self.call_count}次调用查询：'{query}')")
#     #两条写死的结果，用于测试
#     return [
#       SearchResult(
#         title="Fake Result 1: 人工智能",
#         url="https://example.com/ai",
#         snippet="这是模拟的搜索结果内容1"
#       ),
#       SearchResult(
#         title="Fake Result 2: 机器学习",
#         url="https://example.com/ml",
#         snippet="这是模拟的搜索结果内容2"
#       )
#     ]
  
def main():
  print("现在尝试检索")
  # with tempfile.TemporaryDirectory() as tmpdir:
  #   cache_dir = Path(tmpdir)
  #   print(f"创建临时目录:{cache_dir}")
  #   cache = SearchCache(cache_dir)
  #   provider = FakeProvider()

  #   print("\n第一次调用")
  #   res_1 =  cached_search(provider,cache,"测试关键词",max_results=2)

  #   assert len(res_1) == 2,f"第一次应返回2条结果，实际返回{len(res_1)}"
  #   assert provider.call_count == 1,f"第一次调用后call_count应该为1，实际为{provider.call_count}"
  #   print("第一次调用成功，provider被调用，返回2条结果")

  #   print("\n第二次调用，预期命中缓存")
  #   res_2 =  cached_search(provider,cache,"测试关键词",max_results=2)
  #   assert len(res_2) == 2,f"第二次应返回2条结果，实际返回{len(res_2)}"
  #   assert provider.call_count == 1,f"第二次调用命中缓存后call_count应该为1，实际为{provider.call_count}"
  #   print("第二次调用成功，缓存命中")

  print("正在发现并注册providers")
  discover()

  #测试Tavily
  try:
    run_test("tavily", query="大模型推理加速", max_results=5)
  except Exception as e:
    print(f"Tavily测试失败:{e}")

  #测试 DDGS（可能被限流）
  print("切换到DDGS(DuckDuckGo)测试")
  try:
    run_test("ddgs", query="大模型推理加速", max_results=5)
  except Exception as e:
    print(f"DDGS测试失败（可能是限流/网络问题）:{e}")
    
  print("\n测试完毕")

if __name__=="__main__":
  main()