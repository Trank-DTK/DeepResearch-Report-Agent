import os
from .registry import register
from ..llm.client import LLMClient

@register("llm","openai_compatible")
def build(cfg:dict) -> LLMClient:
  #提取API Key
  env_key_name = cfg.get("api_key_env","")
  if env_key_name:
    api_key = os.getenv(env_key_name)
    if not api_key:
      raise ValueError(
        "环境变量未设置或为空，请在.env文件中配置"
      )
  else:
    api_key = cfg.get("api_key","ollama")
  
  base_url = cfg["base_url"]
  model = cfg["model"]
  temperature = cfg.get("temperature",0.2)
  max_retries = cfg.get("max_retries",3)
  timeout = cfg.get("timeout",60.0)

  return LLMClient(
    base_url=base_url,
    api_key=api_key,
    model=model,
    temperature=temperature,
    max_retries=max_retries,
    timeout=timeout
  )