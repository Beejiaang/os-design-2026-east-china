"""Build the editable report from its reviewed Markdown source.

Authoring dependency: python-docx (not a runner dependency). Render and inspect
all pages after changing this builder or the report source.
"""
import argparse
import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/implementation/design-and-test-report.md"
OUTPUT = ROOT / "demo/delivery/设计与测试报告_RC1.docx"


def shade(cell, fill):
    props = cell._tc.get_or_add_tcPr()
    item = OxmlElement("w:shd")
    item.set(qn("w:fill"), fill)
    props.append(item)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--release-label", default="RC1")
    args = parser.parse_args()
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.5), Inches(11)
    section.top_margin = section.bottom_margin = Inches(.7)
    section.left_margin = section.right_margin = Inches(.8)
    for name in ("Normal", "Title", "Subtitle", "Heading 1", "Heading 2"):
        style = doc.styles[name]
        style.font.name = "Microsoft YaHei"
        style._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        style.font.color.rgb = RGBColor(0, 0, 0)
    normal = doc.styles["Normal"]
    normal.font.size = Pt(11)
    normal.paragraph_format.line_spacing = 1.2
    normal.paragraph_format.space_after = Pt(8)
    doc.styles["Title"].font.size = Pt(21)
    doc.styles["Title"].paragraph_format.space_after = Pt(16)
    doc.styles["Heading 1"].font.size = Pt(16)
    doc.styles["Heading 1"].paragraph_format.space_after = Pt(12)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)
    lines = args.source.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if line == "<!-- pagebreak -->":
            doc.add_page_break()
        elif line.startswith("# "):
            doc.add_paragraph(line[2:], "Title")
        elif line.startswith("## "):
            doc.add_paragraph(line[3:], "Heading 1")
        elif line.startswith("!["):
            match = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", line)
            if not match:
                raise ValueError("Invalid image line: " + line)
            doc.add_picture(str(args.source.parent / match[2]), width=Inches(6.5))
            doc.add_paragraph(match[1]).paragraph_format.space_after = Pt(6)
        elif line.startswith("```"):
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(3)
                run = p.add_run(lines[index])
                run.font.name, run.font.size = "Consolas", Pt(9)
                index += 1
        elif line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                values = [v.strip() for v in lines[index].strip("|").split("|")]
                if not all(set(v) <= set("-: ") for v in values):
                    rows.append(values)
                index += 1
            table = doc.add_table(rows=0, cols=len(rows[0]))
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.autofit = False
            widths = ({3: [1.45, 1.65, 3.8], 4: [2.6, 1.1, 1.6, 1.6]}).get(
                len(rows[0]), [6.9 / len(rows[0])] * len(rows[0]))
            for col, width in zip(table.columns, widths):
                col.width = Inches(width)
            for ri, values in enumerate(rows):
                cells = table.add_row().cells
                for ci, (cell, value) in enumerate(zip(cells, values)):
                    cell.width = Inches(widths[ci])
                    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    props = cell._tc.get_or_add_tcPr()
                    borders = OxmlElement("w:tcBorders")
                    for side in ("top", "left", "bottom", "right"):
                        border = OxmlElement("w:" + side)
                        for key, val in (("val", "single"), ("sz", "4"), ("color", "D9D9D9")):
                            border.set(qn("w:" + key), val)
                        borders.append(border)
                    props.append(borders)
                    margins = OxmlElement("w:tcMar")
                    for side in ("top", "left", "bottom", "right"):
                        item = OxmlElement("w:" + side)
                        item.set(qn("w:w"), "90")
                        item.set(qn("w:type"), "dxa")
                        margins.append(item)
                    props.append(margins)
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.line_spacing = 1.1
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 or len(value) > 15 else WD_ALIGN_PARAGRAPH.CENTER
                    r = p.add_run(value)
                    r.font.size = Pt(9.5)
                    r.bold = ri == 0
                    if ri == 0:
                        r.font.color.rgb = RGBColor(255, 255, 255)
                    shade(cell, "243B53" if ri == 0 else ("F2F5F7" if ri % 2 else "FFFFFF"))
                no_split = OxmlElement("w:cantSplit")
                table.rows[-1]._tr.get_or_add_trPr().append(no_split)
                if ri == 0:
                    table.rows[-1]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
            doc.add_paragraph().paragraph_format.space_after = Pt(0)
            continue
        elif line:
            doc.add_paragraph(line)
        index += 1
    doc.core_properties.title = "面向 openEuler 数据处理任务的 CPU 资源约束与性能回归分析工具设计与测试报告"
    doc.core_properties.author = "项目技术资料整理"
    doc.core_properties.subject = f"候选交付版 {args.release_label} 设计测试与同类工具比较"
    # Remove decorative paragraph borders inherited from the bundled template.
    for element in (doc.styles.element, doc.element):
        for border in list(element.iter(qn("w:pBdr"))):
            border.getparent().remove(border)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
