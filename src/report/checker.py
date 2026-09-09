import logging
import re
from dataclasses import dataclass,field
from pathlib import Path
from .synthesizer import parse_citations


logger = logging.getLogger(__name__)

IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")

@dataclass
class CheckItem:
  level:str   #ok|warn|error
  msg:str

def run_checks(state,min_words:int=2000) -> list[CheckItem]:
  """对RunState做体检"""
  items:list[CheckItem] = []
  total_body = 0

  for section in state.outline:
    sid = section.id
    body = state.section_markdown.get(sid,"")
    total_body += len(body)
    evs = state.evidence_by_section.get(sid,[])
    #结构：正文是否存在且达标
    if not body:
      items.append(CheckItem("error",f"第{sid}章({section.title}):正文缺失"))
    elif len(body) < 300:
      items.append(CheckItem("warn",f"第{sid}章：正文偏短({len(body)}字)"))
    #引用越界检查(防幻觉)
    cited = parse_citations(body)
    ref_ids = {r["id"] for r in getattr(state,"references",[]) or []}
    out_of_range = sorted(n for n in cited if n not in ref_ids)
    if out_of_range:
      items.append(CheckItem("error",f"第{sid}章：引用越界{out_of_range}（全文参考文献{len(ref_ids)}条）"))
    elif cited:
      items.append(CheckItem("ok",f"第{sid}章：引用{sorted(cited)}均在参考文献范围内"))
    
    #图表一致性
    charts = state.chart.get(sid,[])
    for c in charts:
      p = Path(c["path"])
      if not p.exists():
        items.append(CheckItem("error",f"第{sid}章：图表文件缺失{c['path']}"))
      elif c["path"] not in body:
        items.append(CheckItem("warn",f"第{sid}章：图'{c['caption']}'已生成但正文未引用"))
      if not c.get("verified",False):
        items.append(CheckItem("warn",f"第{sid}章：图'{c['caption']}'校验未通过仍被采用"))
    
  #总字数达标
  if total_body < min_words:
    items.append(CheckItem("error",f"正文总字数{total_body}<目标{min_words}"))
  else:
    items.append(CheckItem("ok",f"正文总字数{total_body}>={min_words}"))

  return items


def format_check_report(items:list[CheckItem]) -> str:
  """把体检结果格式化成可打印/可展示的清单"""
  icon = {"ok":"√ ","warn":"⚠ ","error":"× "}
  lines = [f"{icon[i.level]}{i.msg}" for i in items]
  summary = f"共{len(items)}项:"
  for lv in ("ok","warn","error"):
    n = sum(1 for i in items if i.level == lv)
    summary += f"{icon[lv]}{n}"
  return summary + "\n" + "\n".join(lines)









