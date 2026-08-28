from dataclasses import dataclass

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
