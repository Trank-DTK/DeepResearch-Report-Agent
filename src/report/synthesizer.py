import re
from urllib.parse import urlparse
import logging
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_citations(body:str) -> set[int]:
  """从正文提取被引用的编号集合"""
  return {int(n) for n in re.findall(r"\[(\d+)\]",body)}

def clean_title(title:str,url:str) -> str:
  """脏标题兜底"""
  t = (title or "").strip()
  if len(t) < 2 or t == "\\N":
    return urlparse(url).netloc
  return t


def build_reference_section(state,section,body:str) -> str:
  """本章参考来源清单：编号与正文一一对应（按章节内证据编号）"""
  cited = parse_citations(body)  #只列正文真正引用过的
  evs = state.evidence_by_section.get(section.id,[])
  lines = [f"### 第{section.id}章参考来源"]
  for i,e in enumerate(evs,1):
    if i in cited:
      lines.append(f"[{i}]{clean_title(e.title,e.url)} - {e.url}")
  return "\n".join(lines)

def summarize_report(llm_client,section_md:list[str]) -> str:
  """研究摘要：一次LLM调用生成3~5句，失败兜底第一张前200字"""
  try:
    joined = "\n\n".join(s[:500] for s in section_md)
    res = llm_client.chat_json([
      {"role":"system","content":"你是一个研究报告摘要生成器，只输出JSON:{\"summary\":\"3~5句话概括全文核心结论\"}"},
      {"role":"user","content":f"请根据以下内容生成研究报告摘要：\n{joined}"}
    ])
    if res.get("summary"):
      return res["summary"]
  except Exception as e:
    logger.warning("生成研究报告摘要失败: %s ，使用兜底策略",e)
  return section_md[0][:200] if section_md else "（无内容）"

def strip_leading_headings(body:str) -> str:
  """去掉正文开头连续的标题行"""
  lines = body.split("\n")
  while lines and (not lines[0].strip() or lines[0].strip().startswith("#")):
    lines.pop(0)  #开头空行和#开头的行都删掉
  return "\n".join(lines).strip()


def assemble_report(state,llm_client=None)->str:
  """拼装完整的Markdown报告"""
  parts = [f"# {state.topic}",""]

  #摘要
  sections_md = [state.section_markdown.get(s.id,"") for s in state.outline]
  summary = summarize_report(llm_client,[m for m in sections_md if m]) if llm_client else ""
  parts += ["研究摘要:",summary,""]

  #目录
  parts.append("## 目录")
  for s in state.outline:
    parts.append(f"{s.id}.{s.title}")
  parts.append("")

  #正文+参考来源
  for s in state.outline:
    parts.append(f"## {s.id}.{s.title}")
    body = state.section_markdown.get(s.id,"")
    if body:
      body = strip_leading_headings(body)
      parts.append(body)
    else:
      logger.warning("第%d章正文缺失，写入占位",s.id)
      parts.append("（本章生成失败，证据不足或循环超限）")
    parts.append("")
    parts.append(build_reference_section(state,s,body))
    parts.append("")
  
  return "\n".join(parts)


def save_report(markdown:str,output_dir:Path,topic:str) -> Path:
  """保存markdown报告"""
  output_dir.mkdir(parents=True,exist_ok=True)
  path = output_dir / f"report_{hashlib.md5(topic.encode()).hexdigest()}.md"
  path.write_text(markdown,encoding="utf-8")
  logger.info("报告已保存: %s（%d字）",path,len(markdown))
  return path
