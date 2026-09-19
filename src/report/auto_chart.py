import logging
from pathlib import Path
from .chart import render_chart,pick_chart_type
from .verify import verify_chart_text
from .synthesizer import parse_citations

logger = logging.getLogger(__name__)

FIND_PROMPT = """你是图表数据规划大师。根据章节正文与证据，判断是否适合配一张数据图。
仅当正文/证据中存在2个以上可对比的具体数值（性能对比、占比、趋势、成本等）时才配图。
图型选择规则（重要）：
1.份额/占比/构成（各部分加总≈100%) → pie
2.随时间/版本/年份变化的趋势 → line
3.并列方案之间的数值对比 → bar
4.全文图型应尽量多样：若某类型已被使用过，优先改用尚未出现的类型（除非数据形态确实不适合）
只输出JSON: {"need_chart":true或false,"chart_type":"bar|line|pie",
"title":"图标题","data":[{"label":"类别","value":数值}],"unit":"单位(可空)"}"""


def auto_illustrate(state,llm_client,chart_cfg:dict) -> int:
  """给没有图的章节自动配图。返回成功配图数，每章最多1张图"""
  made = 0
  out_dir = Path(chart_cfg.get("output_dir","data/chart"))

  for section in state.outline:
    sid = section.id
    if state.chart.get(sid):
      continue
    body = state.section_markdown.get(sid,"")
    evs = state.evidence_by_section.get(sid,[])
    if not body or not evs:
      continue

    #Find（把全文已用图型统计注入，引导图型多样）
    used = {}
    for charts in state.chart.values():
      for c in charts:
        t = c.get("chart_type","")
        used[t] = used.get(t,0) + 1
    evidence_clip = "\n".join(f"[{i}]{e.title}...{e.content[:150]}" for i,e in enumerate(evs,1))
    try:
      res = llm_client.chat_json([
        {"role":"system","content":FIND_PROMPT},
        {"role":"user","content":f"章节标题{section.title}\n章节正文：{body[:800]}\n"
                                 f"证据摘要：\n{evidence_clip[:2000]}\n"
                                 f"本篇已使用的图表类型统计：{used or '{}'}（请优先选择尚未使用的类型）"},
      ])
    except Exception as e:
      logger.warning("第%d章配图规划失败，跳过：%s",sid,e)
      continue
    if not res.get("need_chart"):
      logger.info("第%d章无需配图",sid)
      continue
    data = res.get("data") or []
    if len(data) < 2:
      logger.info("第%d章配图数量不足，跳过",sid)
      continue
    
    try:
      _labels = [str(d.get("label","")) for d in data]
      _values = [float(d.get("value")) for d in data]
      picked = pick_chart_type(_labels,_values,used)
      if picked != res.get("chart_type"):
        logger.info("第%d章图型由代码调整：%s → %s",sid,res.get("chart_type"),picked)
      res["chart_type"] = picked
    except (TypeError,ValueError):
      pass
    #Draw
    out_path = out_dir / f"s{sid}_auto.png"
    err = render_chart(res.get("chart_type","bar"),res.get("title","数据图"),data,out_path)
    if err:
      logger.warning("第%d章自动配图失败:%s",sid,err)
      continue

    #Verify
    verdict = {"consistent":True}
    if chart_cfg.get("verify_mode","text") == "text":
      verdict = verify_chart_text(llm_client,res.get("chart_type","bar"),res.get("title",""),data)
    if not verdict.get("consistent",True):
      logger.warning("第%d章自动配图校验未通过",sid)

    posix = out_path.as_posix()
    state.section_markdown[sid] = body.rstrip() + f"\n\n![{res.get('title','数据图')}]({posix})\n"
    state.chart.setdefault(sid,[]).append({"path":posix,"caption":res.get("title", ""),"chart_type":res.get("chart_type","bar"),"verified":verdict.get("consistent",True),"auto":True})

    logger.info("第%d章自动配图成功:%s", sid,posix)
    made+=1
    
  return made




































