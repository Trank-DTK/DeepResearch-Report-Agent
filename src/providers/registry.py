from typing import Callable
from pathlib import Path
import importlib.util

REGISTRY:dict = {"llm":{},"search":{},"fetcher":{},"verifier":{}}

#registry装饰器
def register(kind:str,name:str):
  def decorator(func:Callable) -> Callable:
    if kind not in REGISTRY:
      REGISTRY[kind] = {}
    REGISTRY[kind][name] = func
    return func
  return decorator

#动态导入src/providers文件夹中的文件
def discover():
  providers_dir = Path(__file__).parent

  for file_path in providers_dir.glob("*.py"):
    if file_path.name == "__init__.py":
      continue
    module_name = f"src.providers.{file_path.stem}"  #如src.providers.llm_openai
    importlib.import_module(module_name)


def get(kind:str,name:str) -> Callable | None:
  return REGISTRY.get(kind,{}).get(name)
