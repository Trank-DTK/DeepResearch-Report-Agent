import logging
import re
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

CHART_TYPES = {"bar","barh","line","pie"}

#三套配色循环使用，避免全篇同色
PALETTES = [
  ["#4C72B0","#DD8452","#55A868","#C44E52","#8172B3","#937860"],
  ["#2E5E8C","#E1812C","#3A923A","#C03D3E","#9372B4","#845B53"],
  ["#1F77B4","#FF7F0E","#2CA02C","#D62728","#9467BD","#8C564B"],
]


def pick_chart_type(labels:list,values:list,used:dict) -> str:
  """按数据形态确定图型"""
  text = " ".join(str(x) for x in labels)
  has_time = bool(re.search(r"(19|20)\d{2}",text)) or any(
    k in text for k in ("年","月","季度","版本","代际","迭代","轮次","阶段"))
  total = sum(values) or 1
  looks_share = (90 <= total <= 110) or any(
    k in text for k in ("占比","份额","比例","构成","百分比"))
  if has_time:
    prefer = ["line","bar","pie"]
  elif looks_share:
    prefer = ["pie","bar","line"]
  else:
    prefer = ["bar","barh","line","pie"]
  for t in prefer:
    if used.get(t,0) < 2:      #同类型全篇最多2张
      return t
  return prefer[0]


def render_chart(chart_type:str,title:str,data:list[dict],output_dir:Path,palette_idx:int=0) -> str:
  """画图，成功则返回‘’，失败返回错误信息。palette_idx 用于让各图配色不同。"""
  if chart_type not in CHART_TYPES:
    return f"不支持的图表类型{chart_type}，可选：{sorted(CHART_TYPES)}"
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
      return f"第{i+1}个数据点value不是数字:{d.get('value')!r}"
    labels.append(label)
    values.append(value)

  _setup_chinese_font()
  colors = PALETTES[palette_idx % len(PALETTES)]
  fig,ax = plt.subplots(figsize=(7.5,4.8))

  if chart_type == "bar":
    bars = ax.bar(labels,values,color=[colors[i % len(colors)] for i in range(len(labels))])
    ax.bar_label(bars,fmt="%.2f",fontsize=9,padding=2)   #柱顶标数值
    ax.grid(axis="y",linestyle="--",alpha=0.4)
    ax.tick_params(axis="x",rotation=15)
    ax.set_ylabel("数值")
  elif chart_type == "barh":
    ylabels,yvalues = labels[::-1],values[::-1]          #水平条形：标签长时更易读
    bars = ax.barh(ylabels,yvalues,color=[colors[i % len(colors)] for i in range(len(ylabels))])
    ax.bar_label(bars,fmt="%.2f",fontsize=9,padding=2)
    ax.grid(axis="x",linestyle="--",alpha=0.4)
    ax.set_xlabel("数值")
  elif chart_type == "line":
    xs = list(range(len(labels)))
    ax.plot(xs,values,marker="o",markersize=6,linewidth=2,color=colors[0])
    ax.fill_between(xs,values,alpha=0.15,color=colors[0])  #面积填充
    ax.set_xticks(xs)
    ax.set_xticklabels(labels,rotation=15)
    ax.grid(axis="y",linestyle="--",alpha=0.4)
    ax.set_ylabel("数值")
  else:
    wedges,_texts,autotexts = ax.pie(
      values,autopct="%.1f%%",startangle=90,pctdistance=0.78,
      colors=[colors[i % len(colors)] for i in range(len(values))],
      wedgeprops={"width":0.45,"edgecolor":"white","linewidth":1.5}) #环形
    for t in autotexts:
      t.set_fontsize(9)
    ax.legend(wedges,labels,loc="center left",bbox_to_anchor=(1.0,0.5),fontsize=9)

  ax.set_title(title,fontsize=12,pad=12,fontweight="bold")
  output_dir.parent.mkdir(parents=True,exist_ok=True)
  fig.tight_layout()
  fig.savefig(output_dir,dpi=150,bbox_inches="tight")
  plt.close(fig)
  logger.info("图表已生成:%s",output_dir)
  return ""