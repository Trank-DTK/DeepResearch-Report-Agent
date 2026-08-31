import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

#获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

def load_yaml_config() -> dict:
  """加载项目config.yaml文件以及.env文件"""
  env_path = PROJECT_ROOT / ".env"
  if env_path.exists():
    load_dotenv(env_path)

  config_path = PROJECT_ROOT / "config.yaml"
  if not config_path.exists():
    raise FileNotFoundError(f"配置文件不存在：{config_path}")
  with open(config_path,"r",encoding="utf-8") as f:
    config = yaml.safe_load(f)
  return config

def get_llm_config() -> dict:
  """转换为字典格式"""
  full_config = load_yaml_config()
  llm_cfg = full_config.get("llm",{})
  return {
    "base_url":llm_cfg.get("base_url"),
    "model":llm_cfg.get("model"),
    "api_key_env":llm_cfg.get("api_key_env"),
    "temperature":llm_cfg.get("temperature",0.2),
    "max_retries":llm_cfg.get("max_retries",3),
    "provider":llm_cfg.get("provider"),
    "timeout":llm_cfg.get("timeout",60.0),
  }

def get_search_config() -> dict:
  """转换为字典格式"""
  full_config = load_yaml_config()
  sc = full_config.get("search",{})
  return {
    "provider":sc.get("provider"),
    "tavily_api_key_env": sc.get("tavily_api_key_env"),
    "max_results": sc.get("max_results", 5),
    "cache_dir": sc.get("cache_dir", "data/cache/search"),
    "timeout": sc.get("timeout", 15.0)
  }

def get_fetcher_config() -> dict:
  full_config = load_yaml_config()
  fc = full_config.get("fetcher",{})
  return {
    "timeout":fc.get("timeout",10),
    "user_agent":fc.get("user_agent"),
    "max_concurrency":fc.get("max_concurrency",5)
  }
