import logging
from pathlib import Path
from src.agent.state import RunState,Evidence
from src.agent.planner import OutlineSection
from src.report.checker import run_checks,format_check_report

logging.basicConfig(level=logging.INFO,format="%(levelname)s %(name)s:%(message)s")

def main():
    print("开始测试")
    outline = [
        OutlineSection(id=1,title="硬件方案",question="硬件方案有哪些？",keywords=["GPU"]),
        OutlineSection(id=2,title="模型压缩",question="压缩方法有哪些？",keywords=["剪枝"]),
    ]

    evs1 = [Evidence(url=f"https://example.com/{i}",title=f"证据{i}",content=f"这是第{i}条证据的正文。" * 20) for i in range(1,4)]   #3条证据
    evs2 = [Evidence(url="https://example.com/only",title="唯一证据",content="唯一证据内容。" * 20)] #1条证据
    body1 = "硬件方案主要有GPU与TPU两类[1]，各有优劣[2][3]。\n" * 15   #≥300字，引用[1][2][3]全部合法
    body2 = "模型压缩包括剪枝[5]。\n" * 8                              #引用[5]越界且正文偏短

    real = next((p for p in ["data/chart/s1_f1.png","data/chart/s1_f2.png","data/chart/smoke_bar.png"] if Path(p).exists()), None)
    charts2 = [{"path":"data/chart/no_such.png","caption":"缺失图","chart_type":"bar","verified":True},]
    if real:
        charts2 += [
            {"path":real,"caption": "正文未引用的图","chart_type":"bar","verified": True}, #生成了但正文没引用
            {"path":real,"caption": "未过校验的图","chart_type":"bar","verified": False}, #校验没过还用
        ]
    else:
        print("警告：没有可用真实图")

    state = RunState(
        topic="自检器测试",
        outline=outline,
        evidence_by_section={1:evs1, 2:evs2},
        section_markdown={1:body1,2:body2},
        chart={1:[],2:charts2},
    )

    items = run_checks(state,min_words=2000)
    print(format_check_report(items))
    print()

    #每种问题都必须被对应级别抓到
    errs = [i.msg for i in items if i.level == "error"]
    warns = [i.msg for i in items if i.level == "warn"]
    oks = [i.msg for i in items if i.level == "ok"]

    assert any("引用越界" in m for m in errs), "未抓到引用越界"
    assert any("图表文件缺失" in m for m in errs), "未抓到图表文件缺失"
    assert any("总字数" in m for m in errs), "未抓到总字数不足"
    assert any("正文偏短" in m for m in warns), "未抓到正文偏短"
    assert any("均在本章证据范围内" in m for m in oks), "健康章节没得到ok"
    if real:
        assert any("正文未引用" in m for m in warns), "未抓到正文未引用的图"
        assert any("校验未通过" in m for m in warns), "未抓到校验未通过"

    print("全部断言通过：自检器能抓到每一种问题！")

if __name__ == "__main__":
    main()