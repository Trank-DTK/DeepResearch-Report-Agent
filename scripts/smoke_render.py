import logging
from pathlib import Path
from src.report.render import render_report
from src.utils.config import PROJECT_ROOT


logging.basicConfig(level=logging.INFO,format="%(levelname)s %(name)s:%(message)s")

def main():
  out_dir = Path("data/outputs")
  print("开始测试")
  print("用例1（正常用例）")
  md1 = """# 测试报告：大模型推理加速

> 研究摘要：用于验证 HTML 渲染的测试报告。

## 1. 硬件方案对比

主流推理方案的对比如图所示：

![各方案推理吞吐对比](data/chart/s1_f1.png)

## 参考来源

[1] 示例来源 - https://example.com"""
  html1 = render_report(md1,out_dir / "smoke_render_ok.html")
  text1 = html1.read_text(encoding="utf-8")
  assert "data:image/png;base64," in text1,"图片未内嵌未base64"
  assert html1.stat().st_size > 10_000,"HTML太小，图片可能没嵌进去"
  print(f"用例1通过：{html1} ({html1.stat().st_size}字节)")

  print("用例2：引用不存在的图片")
  md2 = md1.replace("s1_f1.png","nofile.png")
  html2 = render_report(md2,out_dir / "smoke_render_false.html")
  text2 = html2.read_text(encoding="utf-8")
  assert "data:image/png;base64," not in text2,"缺失图片不应被内嵌"
  print(f"用例2通过：{html2}")

  import os
  import sys


  tpath = html1.resolve()  #直接转换为绝对路径

  assert tpath.exists(),f"文件不存在:{tpath}"
  if sys.platform == "win32":
    os.startfile(tpath)


if __name__=="__main__":
  main()
  



