import logging
import logging.handlers
import queue
import threading
import time
from pathlib import Path

import streamlit as st

from src.agent.runner import run_full_report
from src.report.checker import format_check_report

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
st.set_page_config(page_title="智绘研报图文报告智能生成系统",page_icon="./images/favicon.ico",layout="wide")

if "logs" not in st.session_state:
  st.session_state.logs = []
if "running" not in st.session_state:
  st.session_state.running = False
if "result" not in st.session_state:
  st.session_state.result = None
if "error" not in st.session_state:
  st.session_state.error = None

#主线程轮询
if st.session_state.running:
  q = st.session_state.get("q")
  while q and not q.empty():
    item = q.get_nowait()
    if isinstance(item,tuple) and item[0] == "RESULT":
      st.session_state.result = item[1]
      st.session_state.running = False
    elif isinstance(item,tuple) and item[0] == "ERROR":
      st.session_state.error = item[1]
      st.session_state.running = False
    else:
      st.session_state.logs.append(item)

class QueueLogHandler(logging.Handler):
  """把日志格式化成字符串后放入queue"""
  def __init__(self,q:queue.Queue):
    super().__init__()
    self.q = q
  def emit(self,record):
    try:
      self.q.put(self.format(record))
    except Exception:
      pass




#后台线程
def _worker(topic:str,q:queue.Queue):
  handler = QueueLogHandler(q)
  handler.setFormatter(logging.Formatter("%(levelname)s %(name)s:%(message)s"))
  logging.getLogger().addHandler(handler)
  try:
    res = run_full_report(topic)
    q.put(("RESULT",res))
  except Exception as e:
    q.put(("ERROR",str(e)))
  finally:
    logging.getLogger().removeHandler(handler)

st.title("智绘研报图文报告智能生成系统")
st.caption("输入研究问题即可生成图文结合的报告")

topic = st.text_input("研究问题",value="大模型推理加速的主流技术路线有哪些？")

col1,col2 = st.columns([1,4])
with col1:
  start = st.button("开始生成",disabled=st.session_state.running,type="primary")
with col2:
  if st.session_state.running:
    st.caption("运行中...运行期间请勿关闭页面！")
  else:
    st.caption("Agent已就绪")

if start and topic.strip():
  st.session_state.logs = []
  st.session_state.result = None
  st.session_state.error = None
  st.session_state.running = True
  st.session_state.q = queue.Queue()
  threading.Thread(target=_worker,args=(topic.strip(),st.session_state.q),daemon=True).start()


if st.session_state.logs:
  with st.expander("运行日志",expanded=st.session_state.running):
    st.code("\n".join(st.session_state.logs[-80:]),language="text")

#状态分流
if st.session_state.error:
  st.error(f"运行出错：{st.session_state.error}")
  st.stop()
elif st.session_state.result:
  r = st.session_state.result
  st.success(f"生成完成，耗时{r['elapsed']:.1f}秒，共{r['num_sections']}章")
  st.markdown("### 质量自检")
  st.code(format_check_report(r["checks"]), language="text")

  tab_md, tab_html = st.tabs(["Markdown","HTML 预览"])
  with tab_md:
    st.download_button("下载 Markdown",r["report"],file_name=r["md_path"].name,mime="text/markdown")
    st.markdown(r["report"][:3000])
  with tab_html:
    html_text = r["html_path"].read_text(encoding="utf-8")
    st.download_button("下载 HTML",html_text,file_name=r["html_path"].name,mime="text/html")
    st.components.v1.html(html_text, height=800, scrolling=True)
elif st.session_state.running:
  time.sleep(1)
  st.rerun()
else:
  st.info("输入问题后点击[开始生成]按钮")



