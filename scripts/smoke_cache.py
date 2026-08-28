import tempfile
from pathlib import Path
from src.retrieval.cache import SearchCache,cached_search
from src.retrieval.search import SearchResult,SearchProvider


class FakeProvider(SearchProvider):
  """模拟的搜索供应商"""
  def __init__(self):
    self.call_count = 0
  
  def search(self,query:str,max_results:int) -> list[SearchResult]:
    self.call_count += 1
    print(f"[FakeProvider]第{self.call_count}次调用查询：'{query}')")
    #两条写死的结果，用于测试
    return [
      SearchResult(
        title="Fake Result 1: 人工智能",
        url="https://example.com/ai",
        snippet="这是模拟的搜索结果内容1"
      ),
      SearchResult(
        title="Fake Result 2: 机器学习",
        url="https://example.com/ml",
        snippet="这是模拟的搜索结果内容2"
      )
    ]
  
def main():
  print("现在尝试检索")
  with tempfile.TemporaryDirectory() as tmpdir:
    cache_dir = Path(tmpdir)
    print(f"创建临时目录:{cache_dir}")
    cache = SearchCache(cache_dir)
    provider = FakeProvider()

    print("\n第一次调用")
    res_1 =  cached_search(provider,cache,"测试关键词",max_results=2)

    assert len(res_1) == 2,f"第一次应返回2条结果，实际返回{len(res_1)}"
    assert provider.call_count == 1,f"第一次调用后call_count应该为1，实际为{provider.call_count}"
    print("第一次调用成功，provider被调用，返回2条结果")

    print("\n第二次调用，预期命中缓存")
    res_2 =  cached_search(provider,cache,"测试关键词",max_results=2)
    assert len(res_2) == 2,f"第二次应返回2条结果，实际返回{len(res_2)}"
    assert provider.call_count == 1,f"第二次调用命中缓存后call_count应该为1，实际为{provider.call_count}"
    print("第二次调用成功，缓存命中")

  print("\n测试完毕")

if __name__=="__main__":
  main()