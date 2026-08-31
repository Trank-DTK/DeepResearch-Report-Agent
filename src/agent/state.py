from dataclasses import dataclass,asdict
import json
from datetime import datetime
from pathlib import Path
import hashlib

@dataclass
class Evidence:
  url:str
  title:str
  content:str
  source_query:str = ""
  section_id:str = ""
  provider:str = ""
  fetched_at:str = ""
  degraded:bool = False


def save_evidence(evidence_list:list[Evidence],output_dir:Path,topic:str) -> Path:
  topic_md5 = hashlib.md5(topic.encode()).hexdigest()
  filename = f"evidence_{topic_md5}.json"
  file_path = output_dir / filename
  success_fetch = 0   #抓取成功
  degraded = 0 #摘要兜底
  sum_character = 0
  for e in evidence_list:
    if e.content and not e.degraded:
      success_fetch += 1
      sum_character += len(e.content)
    elif e.degraded:
      degraded += 1
  
  average_char = (sum_character / success_fetch) if success_fetch else 0

  output_dir.mkdir(parents=True,exist_ok=True)
  data = [asdict(e) for e in evidence_list]
  with open(file_path,"w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)

  print(f"[证据保存]文件: {file_path}")
  print(f"总证据数: {len(evidence_list)}")
  print(f"正文抓取成功: {success_fetch} | 摘要兜底:{degraded} ")
  print(f"平均正文长度: {average_char:.0f} 字")

  return file_path

