import os
from pathlib import Path
from src.report.chart import render_chart

data_true = [{"label":"deepseek模型","value":15.8},{"label":"GLM模型","value":18.1},{"label":"ChatGPT模型","value":12.8}]
data_true_pie = [{"label":"deepseek模型","value":0.2},{"label":"GLM模型","value":0.45},{"label":"ChatGPT模型","value":0.35}]
data_false_value = [{"label":"deepseek模型","value":"abc"},{"label":"GLM模型","value":18.1},{"label":"ChatGPT模型","value":12.8}]
data_false_one = [{"label":"GLM模型","value":18.1}]


def main():
  print("开始生图测试")
  file_path_bar = Path("data/chart/smoke_bar.png")
  render_chart("bar",title="各类主流模型的某自定义属性比较",data=data_true,output_dir=file_path_bar)
  size_bytes = os.path.getsize(file_path_bar)
  if not size_bytes or size_bytes == 0:
    print("柱状图生成失败")
  print(f"柱状图生成成功，图片大小{size_bytes}字节")

  file_path_line = Path("data/chart/smoke_line.png")
  render_chart("line",title="各类主流模型的某自定义属性比较",data=data_true,output_dir=file_path_line)
  size_bytes2 = os.path.getsize(file_path_line)
  if not size_bytes2 or size_bytes2 == 0:
    print("折线图生成失败")
  print(f"折线图生成成功，图片大小{size_bytes2}字节")

  file_path_pie = Path("data/chart/smoke_pie.png")
  render_chart("pie",title="各类主流模型的某自定义属性比较",data=data_true_pie,output_dir=file_path_pie)
  size_bytes3 = os.path.getsize(file_path_pie)
  if not size_bytes3 or size_bytes3 == 0:
    print("饼状图生成失败")
  print(f"饼状图生成成功，图片大小{size_bytes3}字节")

  print("开始测试异常用例")
  print("异常1：value中出现'abc'")
  file_path_value = Path("data/chart/smoke_false_value.png")
  err = render_chart("bar",title="各类主流模型的某自定义属性比较",data=data_false_value,output_dir=file_path_value)
  if err:
    print(f"成功出现异常：{err}")
  else:
    print("?为什么会成功呢")

  print("异常2：只有1个点")
  file_path_one = Path("data/chart/smoke_false_one.png")
  err2 = render_chart("bar",title="各类主流模型的某自定义属性比较",data=data_false_one,output_dir=file_path_one)
  if err2:
    print(f"成功出现异常：{err2}")
  else:
    print("?为什么会成功呢")

  print("异常3：图表类型错误")
  file_path_type = Path("data/chart/smoke_false_type.png")
  err3 = render_chart("scatter",title="各类主流模型的某自定义属性比较",data=data_true,output_dir=file_path_type)
  if err3:
    print(f"成功出现异常：{err3}")
  else:
    print("?为什么会成功呢")

  print("测试完毕")

if __name__=="__main__":
  main()
