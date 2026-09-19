"""软著材料：源程序导出（前后各 30 页，每页 50 行；总页数不足 60 页则全部提交）。

用法: python scripts/export_source.py

说明：
- 产物为 UTF-8 带 BOM，避免 Word 误判编码导致中文乱码。
- EXCLUDE 中的文件不参与导出：本脚本自身属于"生成工具"，
  提交软著前会删除，因此一并排除，保证材料与提交内容一致。
- 导出文件含"—— 第 N 页 ——"标记（仅作页数核对用）：
  在 Word 中排版时请用「查找替换 → 通配符」把它们替换为空，
  不要替换成 ^m（分页符），否则会多占一行导致页数翻倍。
"""
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "soft_copyright"
LINES_PER_PAGE, PAGES = 50, 30
PER_PART = LINES_PER_PAGE * PAGES  # 1500 行 = 30 页

# 不参与导出的文件（相对项目根目录，正斜杠）
EXCLUDE = {
    "scripts/export_source.py",   # 生成工具自身，提交前会删除
}


def collect_lines() -> list[str]:
    lines = []
    files = sorted(ROOT.glob("src/**/*.py")) + sorted(ROOT.glob("scripts/*.py"))
    files = [
        f for f in files
        if "__pycache__" not in str(f)
        and f.relative_to(ROOT).as_posix() not in EXCLUDE
    ]
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        lines.append(f"# ==================== 文件: {rel} ====================")
        lines += f.read_text(encoding="utf-8").splitlines()
        lines.append("")

    kept = [f.relative_to(ROOT).as_posix() for f in files]
    print(f"纳入导出的文件数: {len(kept)}")
    for name in kept:
        print(f"  - {name}")
    return lines


def write_paged(lines: list[str], path: Path, start_page: int = 1) -> int:
    """按每页 50 行写出，页尾插入页码标记。返回页数。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    out, page = [], start_page
    for i, line in enumerate(lines):
        out.append(line)
        if (i + 1) % LINES_PER_PAGE == 0:
            out.append(f"—— 第 {page} 页 ——")
            page += 1
    out.append(f"—— 第 {page} 页 ——")  # 末页（不足 50 行也标页）
    # utf-8-sig：带 BOM，Word 打开中文不乱码
    path.write_text("\n".join(out), encoding="utf-8-sig")
    return page - start_page + 1


def main():
    lines = collect_lines()
    total = len(lines)
    pages = (total + LINES_PER_PAGE - 1) // LINES_PER_PAGE
    print(f"\n源文件总行数: {total}（约 {pages} 页）")

    if total <= PER_PART * 2:  # 不足 60 页 → 全部提交
        n = write_paged(lines, OUT / "源代码_全部.txt")
        print(f"✅ 总页数 {pages} ≤ 60，已导出全部：源代码_全部.txt（{n} 页）")
    else:
        n1 = write_paged(lines[:PER_PART], OUT / "源代码_前30页.txt", 1)
        n2 = write_paged(lines[-PER_PART:], OUT / "源代码_后30页.txt", 31)
        print(f"✅ 已导出：前30页.txt（{n1} 页）+ 后30页.txt（{n2} 页，页码从 31 续）")
    print(f"产物目录: {OUT}")


if __name__ == "__main__":
    main()
