import json
import hashlib
from pathlib import Path
from .search import SearchResult,SearchProvider
from dataclasses import asdict

class SearchCache:
  def __init__(self,cache_dir:Path):
    self.cache_dir = cache_dir
    self.cache_dir.mkdir(parents=True,exist_ok=True)  #检查并创建

  def _key(self,query:str,max_results:int,provider_name:str) -> str:
    """根据查询词和最大结果数生成唯一文件名"""
    raw = f"{provider_name}|{query}|{max_results}"
    return hashlib.md5(raw.encode()).hexdigest() #先转换为哈希值，再转换为16进制
  
  def _get_file_path(self,query:str,max_results:int,provider_name:str) -> Path:
    filename = f"{self._key(query,max_results,provider_name)}.json"
    return self.cache_dir / filename
  
  def get(self,query:str,max_results:int,provider_name:str) -> list[SearchResult] | None:
    """从缓存中读取数据"""
    file_path = self._get_file_path(query,max_results,provider_name)

    if not file_path.exists():
      return None
    try:
      with open(file_path,"r",encoding="utf-8") as f:
        data = json.load(f)
      return [SearchResult(**item) for item in data]
    except (json.JSONDecodeError,KeyError,TypeError) as e:
      print(f"缓存文件读取失败（{file_path}）:{e}")
      return None
  
  def set(self,query:str,max_results:int,results:list[SearchResult],provider_name:str) -> None:
    """将数据放入缓存"""
    file_path = self._get_file_path(query,max_results,provider_name)
    data = [asdict(r) for r in results]
    with open(file_path,"w",encoding="utf-8") as f:
      json.dump(data,f,ensure_ascii=False,indent=2)
  
def cached_search(provider:SearchProvider,cache:SearchCache,query:str,max_results:int=5) -> list[SearchResult]:
  """缓存命中机制"""
  provider_name = getattr(provider,"name","unknown")
  cached_result = cache.get(query,max_results,provider_name)
  #命中缓存
  if cached_result:
    return cached_result
  #未命中
  res = provider.search(query,max_results)
  cache.set(query,max_results,res,provider_name)
  return res

def search_multi(primary:SearchProvider,extra:list[SearchProvider],cache,query:str,max_results:int=5) -> list[SearchResult]:
  """主检索器+附加检索器（如arXiv）"""
  results = []
  for p in [*extra,primary]:
    results += cached_search(p,cache,query,max_results)
  return results