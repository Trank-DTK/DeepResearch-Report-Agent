import base64
import logging
import re
from pathlib import Path
import markdown

from src.utils.config import PROJECT_ROOT

logger = logging.getLogger(__name__)

REPORT_CSS = """
body { font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
       max-width: 900px; margin: 0 auto; padding: 24px 32px; color: #222; line-height: 1.75; }
h1 { text-align: center; border-bottom: 3px solid #1f4e79; padding-bottom: 12px; color: #1f4e79; }
h2 { color: #1f4e79; border-left: 5px solid #1f4e79; padding-left: 10px; margin-top: 32px; }
h3 { color: #333; margin-top: 22px; }
blockquote { background: #f4f6f9; border-left: 4px solid #4c72b0;
             margin: 12px 0; padding: 10px 16px; color: #444; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; }
th { background: #eef2f7; }
img { max-width: 100%; height: auto; display: block; margin: 12px auto; }
code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-size: 90%; }
pre { background: #f6f8fa; padding: 12px; border-radius: 5px; overflow-x: auto; }
@media print { body { max-width: none; } h2 { page-break-after: avoid; } }
"""

IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

def embed_images(md_text:str) -> str:
  """将md中的本地图片转换为base64 data URI"""
  def _replace(m:re.Match) -> str:
    alt,src = m.group(1),m.group(2).strip()
    if src.startswith(("http://","https://","data:")):
      return m.group(0)
    p = (PROJECT_ROOT / src).resolve()
    if not p.exists():
      logger.warning("图片不存在，保留原路径:%s",src)
      return m.group(0)
    try:
      b64 = base64.b64encode(p.read_bytes()).decode()
      return f"![{alt}](data:image/png;base64,{b64})"
    except Exception as e:
      logger.warning("图片读取失败 %s:%s",src,e)
      return m.group(0)
  return IMG_RE.sub(_replace,md_text)
  
def render_report(md_text:str,out_path:Path) -> Path:
  """md→单文件HTML"""
  md_text = embed_images(md_text)
  body = markdown.markdown(md_text,extensions=["tables","fenced_code","sane_lists"])
  html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>智绘研报图文报告智能生成系统</title>
<style>{REPORT_CSS}</style>
</head>
<body>
{body}
</body>
</html>"""
  out_path.parent.mkdir(parents=True,exist_ok=True)
  out_path.write_text(html,encoding="utf-8")
  logger.info("HTML报告已生成:%s",out_path)
  return out_path
