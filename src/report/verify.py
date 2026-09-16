import json
import logging

logger = logging.getLogger(__name__)

VERIFY_PROMPT = """你是图表数据一致性校验员。给定图表数据与标题，检查：
1.数值是否像真实数据（有无异常巨大、全相等、比例异常等）
2.标题与数据内容是否相符
只输出JSON: {"consistent": true或false, "issues": ["问题列表"], "suggestion": "修正建议"}"""

def verify_chart_text(llm_client,chart_type:str,title:str,data:list[dict]) -> dict:
  """文本级校验"""
  try:
    payload = json.dumps(data,ensure_ascii=False)
    res = llm_client.chat_json([
      {"role":"system","content":f"{VERIFY_PROMPT}\n图表数据：{payload}\n图表标题：{title}"},
      {"role":"user","content":f"图表类型：{chart_type}"}
    ])
    return {"consistent":bool(res.get("consistent",True)),
            "issues":res.get("issues",[]),
            "suggestion":res.get("suggestion","")}
  except Exception as e:
    logger.warning("图表校验服务异常，放行:%s",e)
    return {"consistent":True,"issues":[],"suggestion":""}
  



