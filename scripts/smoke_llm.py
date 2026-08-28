import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
  sys.path.insert(0,str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from src.utils.config import get_llm_config
from src.providers.registry import discover,get

def main():
  print("测试开始：")
  print("正在发现并注册providers:")
  discover()

  builder = get("llm","openai_compatible")
  if not builder:
    print("未找到‘openai_compatible’构建器")
    return
  
  print("正在加载配置")
  try:
    cfg = get_llm_config()
    print(f"配置为base_url={cfg['base_url']},model={cfg['model']}")
  except Exception as e:
    print(f"配置加载失败：{e}")
    return 
  
  print("正在构建客户端")
  try:
    client = builder(cfg)
    print("客户端构建成功")
  except Exception as e:
    print(f"客户端配置失败：{e}")
    return
  
  print("\n测试用例1：chat对话")
  try:
    res1 = client.chat([{"role":"user","content":"用一句话介绍你自己"}])
    print(f"回复：{res1}\n")
  except Exception as e:
    print(f"用例1失败:{e}")
  
  print("\n测试用例2：JSON输出")
  try:
    res2 = client.chat_json([{"role":"user","content":"请输出{'lang':'中文','year':2026}"}])
    print(f"解析出的字典：{res2}")
    print(f"类型:{type(res2)}")
  except Exception as e:
    print(f"用例2失败：{e}")

  print("用例3：容错测试(先解释再输出JSON)")
  try:
    res3 = client.chat_json([{"role":"user","content":"请先输出一句“好的”，再输出{'lang':'中文','year':2026}"}])
    print(f"解析成功！结果：{res3}")
  except Exception as e:
    print(f"用例3失败：{e}")
  print("\n测试完毕")

if __name__=="__main__":
  main()