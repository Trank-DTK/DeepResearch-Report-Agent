import logging
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  #无窗口后端
import matplotlib.pyplot as plt
from matplotlib import font_manager

logger = logging.getLogger(__name__)


def _setup_chinese_font() -> None:
  """中文字体兜底"""
  for name in ["Microsoft YaHei","SimHei","SimSun"]:
    try:
      font_manager.findfont(name,fallback_to_default=False)
      plt.rcParams["font.sans-serif"] = [name,"DejaVu Sans"]
      plt.rcParams["axes.unicode_minus"] = False #负号不乱码
      return
    except Exception:
      continue
  logger.warning("未找到中文字体，图表中文可能显示错误")

CHART_TYPES = {"bar","line","pie"}

def render_chart(chart_type:str,title:str,data:list[dict],output_dir:Path) -> str:
  """画图，成功则返回‘’，失败返回错误信息"""
  if chart_type not in CHART_TYPES:
    return f"不支持的图表类型 {chart_type} ，可选：{sorted(CHART_TYPES)}"
  if len(data) < 2:
    return "数据不足，至少需要2个数据点"
  labels,values = [],[]
  for i,d in enumerate(data):
    label = str(d.get("label","")).strip()
    if not label:
      return f"第{i+1}个数据点缺少label"
    try:
      value = float(d.get("value"))
    except (TypeError,ValueError):
      return f"第{i+1}个数据点value不是数字:{d.get('value')!r}"   #!r是repr()，显示更全面
    labels.append(label)
    values.append(value)

  _setup_chinese_font()
  fig,ax = plt.subplots(figsize=(7,4.5))
  if chart_type == "bar":
    ax.bar(labels,values,color="#4C7280")
  elif chart_type == "line":
    ax.plot(labels,values,marker="o",color="#C44E52")
  else:
    ax.pie(values,labels=labels,autopct="%.1f%%",startangle=90)

  ax.set_title(title)
  if chart_type != "pie":
    ax.set_ylabel("数值")
    ax.tick_params(axis="x",rotation=15)
    ax.grid(axis="y",alpha=0.3)

  output_dir.parent.mkdir(parents=True,exist_ok=True)
  fig.savefig(output_dir,dpi=150,bbox_inches="tight")
  plt.close(fig)   #释放内存
  logger.info("图表已生成:%s",output_dir)
  return ""


