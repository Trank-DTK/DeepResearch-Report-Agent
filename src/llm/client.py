from openai import OpenAI
import json
import logging

class LLMError(Exception):
  pass

class LLMClient:
  def __init__(self,base_url:str,api_key:str,model:str,temperature:float=0.2,max_retries:int=3,timeout:float=60.0):
    self._client = OpenAI(base_url=base_url,api_key=api_key,
                          timeout=timeout,max_retries=max_retries)
    self.model = model
    self.temperature = temperature
    self.max_retries = max_retries

  def chat(self,messages:list[dict]) -> str:
    res = self._client.chat.completions.create(
      model=self.model,
      temperature=self.temperature,
      messages=messages
    )
    return res.choices[0].message.content
  
  def chat_json(self,message:list[dict]) -> dict:
    msgs = message.copy()
    msgs.insert(0,{"role":"system","content":"只输出JSON，不要解释"})
    last_error = None
    content = ""

    for attempt in range(self.max_retries):
      content = content or ""
      content = self.chat(msgs)

      try:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and start<end:
          json_str = content[start:end+1]
        else:
          #整体解析
          json_str = content
        parsed = json.loads(json_str)
        return parsed
      except json.JSONDecodeError as e:
        last_error = e
        error_msg = f"你上次输出不是合法JSON，错误是{e.msg}，请重新只输出JSON"
        msgs.append({"role":"user","content":error_msg})
        logging.warning(f"JSON 解析失败，第{attempt}次重试:{e}")
        
    raise LLMError(
      f"Failed to get valid JSON after {self.max_retries} attempts. "
      f"Last error:{last_error}"
    )

    















