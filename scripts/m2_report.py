import sys
import logging
from src.report.checker import format_check_report
from src.agent.runner import run_full_report

logging.basicConfig(level=logging.INFO,stream=sys.stdout,format="%(levelname)s %(name)s:%(message)s")

logging.getLogger("httpx").setLevel(logging.WARNING)


def main():
  topic = sys.argv[1] if len(sys.argv) > 1 else "大模型推理加速"
  r = run_full_report(topic)
  print("质量自检：")
  print(format_check_report(r["checks"]))
  print(f"章节数:{r['num_sections']},总字数:{len(r['report'])},"f"证据数:{r['total_evidence']},耗时:{r['elapsed']:.1f}秒")
  print(f"报告:{r['md_path']}")

if __name__=="__main__":
  main()