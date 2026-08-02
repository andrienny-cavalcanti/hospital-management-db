from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports" / "phase-02" / "phase-02-report.md"
OUTPUT = ROOT / "reports" / "phase-02" / "phase-02-report.pdf"


def markdown_inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return text.replace("  ", "<br/>")


def add_header_footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(
        2 * cm,
        A4[1] - 1.15 * cm,
        "Sistema de Gestao Hospitalar - Relatorio da Etapa 2",
    )
    canvas.drawRightString(
        A4[0] - 2 * cm,
        1.1 * cm,
        f"Pagina {document.page}",
    )
    canvas.restoreState()


def build_story(source: str):
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    heading = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        spaceBefore=6,
        spaceAfter=4,
    )
    body = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=12,
        alignment=TA_JUSTIFY,
        spaceAfter=5,
    )
    metadata = ParagraphStyle(
        "ReportMetadata",
        parent=body,
        alignment=TA_CENTER,
        spaceAfter=3,
    )

    story = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph_lines:
            story.append(
                Paragraph(
                    markdown_inline(" ".join(paragraph_lines)),
                    body,
                )
            )
            paragraph_lines.clear()

    for raw_line in source.splitlines():
        line = raw_line.strip()
        if line == "<!-- PAGE BREAK -->":
            flush_paragraph()
            story.append(PageBreak())
        elif line.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(markdown_inline(line[2:]), title))
        elif line.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(markdown_inline(line[3:]), heading))
        elif line.startswith("**Projeto:") or line.startswith("**Banco:") or line.startswith("**Backend:"):
            flush_paragraph()
            story.append(Paragraph(markdown_inline(line), metadata))
        elif not line:
            flush_paragraph()
        else:
            paragraph_lines.append(line)

    flush_paragraph()
    story.append(Spacer(1, 0.1 * cm))
    return story


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.7 * cm,
        title="Relatorio da Etapa 2 - Sistema de Gestao Hospitalar",
        author="Projeto de Banco de Dados",
    )
    document.build(
        build_story(source),
        onFirstPage=add_header_footer,
        onLaterPages=add_header_footer,
    )
    print(f"Relatorio gerado: {OUTPUT}")


if __name__ == "__main__":
    main()
