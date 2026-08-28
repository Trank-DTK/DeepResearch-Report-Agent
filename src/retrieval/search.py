from dataclasses import dataclass
from ..providers.registry import get as get_registry

#SearchResult数据结构
@dataclass
class SearchResult:
  url:str
  title:str
  snippet:str = ""  #片段
  provider:str = ""  

class SearchProvider:
  """检索器基类"""
  def search(self,query:str,max_results:int = 5) -> list[SearchResult]:
    raise NotImplementedError  #子类必须实现search

def build_search_provider(cfg:dict) -> SearchProvider:
  provider_name = cfg.get("provider")
  if not provider_name:
    raise ValueError("配置中缺少'provider'字段，请指定tavily或ddgs")
  builder = get_registry("search",provider_name)
  if not builder:
    raise ValueError(f"未找到搜索供应商'{provider_name}'，请确保该供应商已注册或已被调用")
  return builder(cfg)