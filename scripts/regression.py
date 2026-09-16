"""回归脚本，跑examples/questions.json中的全部题目并记录stats
python scripts/regressions.py --limit 1  可以限制跑问题的数量
"""
import argparse
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0,str(Path(__file__).parent.parent))
from src.agent.runner import run_full_report

ROOT = Path(__file__).parent.parent
OUT_DIR = ROOT / "examples" / "outputs"



def load_questions() -> list[str]:
  data = json.loads((ROOT/"examples"/"questions.json").read_text(encoding="utf-8"))
  return data["questions"]

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--limit",type=int,default=0,help="只跑前N题，N为0时全跑")
  args = parser.parse_args()

  logging.basicConfig(level=logging.WARNING,stream=sys.stdout,format="%(levelname)s %(name)s:%(message)s")
  questions = load_questions()[:args.limit] if args.limit else load_questions()
  OUT_DIR.mkdir(parents=True,exist_ok=True)
  rows = []

  for i,topic in enumerate(questions,1):
    print(f"[{i}/{len(questions)}] {topic}")
    try:
      r = run_full_report(topic)
      ok = sum(1 for c in r["checks"] if c.level == "ok")
      warn = sum(1 for c in r["checks"] if c.level == "warn")
      err = sum(1 for c in r["checks"] if c.level == "error")
      rows.append({"topic":topic,"sections":r["num_sections"],"chars":len(r["report"]),"ok":ok,"warn":warn,
                   "err":err,"elapsed":round(r["elapsed"],1),"md":str(r["md_path"])})
    except Exception as e:
      rows.append({"topic":topic,"error":str(e)})
  print("汇总")
  for row in rows:
    if "error" in row:
      print(f"{row['topic'][:30]}...  ERROR:{row['error'][:80]}")
    else:
      print(f"{row['topic'][:30]}...  {row['sections']}章"
            f"{row['chars']}字 自检{row['ok']}✓/{row['warn']}⚠/{row['err']}✗"
            f"{row['elapsed']}s -> {row['md']}")
  stats_path = OUT_DIR / "regression_stats.json"
  stats_path.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
  print(f"统计结果已保存:{stats_path}")

if __name__=="__main__":
  main()
      


