import sys
from src.agent.planner import plan_outline
from src.utils.config import get_llm_config
from src.providers.registry import discover,get as get_registry



def main():
  topic = sys.argv[1] if len(sys.argv) > 1 else "大模型推理加速"
  print(f"开始收集证据，主题为：{topic}")
  discover()  #发现并注册所有providers
  llm_cfg = get_llm_config()
  builder = get_registry("llm",llm_cfg["provider"])
  if not builder:
    raise ValueError(f"未找到llm构建器: {llm_cfg['provider']}")
  llm_client = builder(llm_cfg)
  res = plan_outline(llm_client,topic)
  print(f"规划得到{len(res)}个章节大纲:")
  for s in res:
    print(f"章节{s.id}: {s.title}, 问题: {s.question}, 关键词: {s.keywords}，关键词（英文）:{s.keywords_en}")
  print("规划章节大纲完成")


if __name__ == "__main__":
  main()