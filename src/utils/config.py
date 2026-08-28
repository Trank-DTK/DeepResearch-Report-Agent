import os
import yaml
from pathlib import Path

#获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

def load_yaml_config() -> dict:
  """加载项目config.yaml文件"""
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

