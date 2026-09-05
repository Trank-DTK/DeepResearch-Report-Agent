from types import SimpleNamespace
from src.agent.state import RunState
from src.agent import tools

def main():
  print("开始测试")
  state = RunState(current_section_id=1)
  ctx = SimpleNamespace(state=state, llm_client=None,
                        chart_cfg={"verify_mode":"text","output_dir":"data/chart"})
  print("测试1：合法用例")
  ok = tools.TOOLS["draw_chart"]({"chart_type":"bar","title":"各方案推理吞吐对比",
        "data":[{"label":"方案A","value":120},{"label":"方案B","value":80},
                 {"label":"方案C","value":95}]},ctx)
  print("用例1:",ok[:80],"...")
  print("用例2：非法数据")
  bad = tools.TOOLS["draw_chart"]({"chart_type":"pie","title":"坏了",
        "data": [{"label":"A","value":"abc"}]},ctx)
  print("用例2:",bad)
  print("用例3：上限测试")
  tools.TOOLS["draw_chart"]({"chart_type":"line","title":"第二张",
        "data":[{"label":"x","value":1}, {"label":"y","value":2}]},ctx)
  third = tools.TOOLS["draw_chart"]({"chart_type": "pie", "title": "第三张",
        "data":[{"label":"a","value":1}, {"label":"b","value":2}]},ctx)
  print("用例3:",third)
  print("state.chart:",state.chart)
  print("测试结束")

if __name__ == "__main__":
  main()