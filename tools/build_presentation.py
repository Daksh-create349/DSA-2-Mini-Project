"""Generate the four-slide presentation PDF from the checked-in project assets."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "presentation" / "range_minimum_presentation.pdf"
WIDTH, HEIGHT = 960, 540

NAVY = colors.HexColor("#172554")
BLUE = colors.HexColor("#2563EB")
ORANGE = colors.HexColor("#EA580C")
GREEN = colors.HexColor("#15803D")
INK = colors.HexColor("#172033")
MUTED = colors.HexColor("#475569")
PALE = colors.HexColor("#F1F5F9")
BORDER = colors.HexColor("#CBD5E1")
WHITE = colors.white


def draw_paragraph(pdf, text, x, top, width, font_size=16, leading=None,
                   color=INK, bold=False, align=TA_LEFT):
    style = ParagraphStyle(
        "slide-text",
        fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=font_size,
        leading=leading or font_size * 1.35,
        textColor=color,
        alignment=align,
        spaceAfter=0,
        spaceBefore=0,
    )
    item = Paragraph(text, style)
    _, height = item.wrap(width, HEIGHT)
    item.drawOn(pdf, x, top - height)
    return top - height


def draw_base(pdf, number, eyebrow, title, subtitle=None):
    pdf.setFillColor(PALE)
    pdf.rect(0, 0, WIDTH, HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(WHITE)
    pdf.roundRect(24, 24, WIDTH - 48, HEIGHT - 48, 14, stroke=0, fill=1)
    pdf.setFillColor(BLUE)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(54, HEIGHT - 52, eyebrow.upper())
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 27)
    pdf.drawString(54, HEIGHT - 88, title)
    if subtitle:
        draw_paragraph(pdf, subtitle, 54, HEIGHT - 117, WIDTH - 110, 11, 14, MUTED)
    pdf.setStrokeColor(BORDER)
    pdf.setLineWidth(0.7)
    pdf.line(54, 51, WIDTH - 54, 51)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(54, 35, "RANGE MINIMUM QUERY  |  CASE STUDY NO. 02")
    pdf.drawRightString(WIDTH - 54, 35, "SLIDE {} OF 4".format(number))


def draw_card(pdf, x, y, width, height, accent=BLUE, fill=WHITE):
    pdf.setFillColor(fill)
    pdf.setStrokeColor(BORDER)
    pdf.setLineWidth(0.8)
    pdf.roundRect(x, y, width, height, 10, stroke=1, fill=1)
    pdf.setFillColor(accent)
    pdf.roundRect(x, y + height - 6, width, 6, 3, stroke=0, fill=1)


def draw_bullet(pdf, text, x, y, width, font_size=12):
    pdf.setFillColor(BLUE)
    pdf.circle(x + 4, y - 6, 3, stroke=0, fill=1)
    return draw_paragraph(pdf, text, x + 15, y, width - 15, font_size,
                          font_size * 1.35, INK)


def draw_cover(pdf):
    draw_base(pdf, 1, "Case Study No. 02  ·  Segment Trees and Sparse Tables",
              "Range Minimum Query with Point Updates")
    draw_paragraph(pdf,
        "A road authority stores a quality score for each road section. "
        "Operators need the lowest score within a range, while new "
        "inspections may change individual scores.",
        58, 405, 430, 16, 23,
    )
    draw_bullet(pdf, "<b>Range query:</b> minimum in inclusive range "
                "<font name='Courier'>[left, right]</font>.", 62, 306, 430, 13)
    draw_bullet(pdf, "<b>Point update:</b> replace the score at one "
                "zero-based index.", 62, 263, 430, 13)
    draw_bullet(pdf, "<b>Goal:</b> compare correctness, speed, update "
                "cost, and memory.", 62, 220, 430, 13)
    draw_card(pdf, 58, 83, 432, 90, BLUE, colors.HexColor("#EFF6FF"))
    draw_paragraph(pdf, "<b>Question</b><br/>Which method stays efficient when "
                   "the scores can change?", 78, 153, 392, 16, 20, NAVY)

    image_path = ROOT / "results" / "road_scenario.png"
    pdf.drawImage(ImageReader(str(image_path)), 530, 239, width=370,
                  height=123, preserveAspectRatio=True, anchor="c", mask="auto")
    draw_paragraph(pdf,
        "<b>Prepared by</b><br/>Daksh Srivastava · Prathamesh More · "
        "Yuvraj Mishra<br/>Biswajeet Rout · Sumit Shingole",
        545, 202, 350, 13, 19, MUTED, align=TA_CENTER,
    )
    pdf.showPage()


def draw_scan_diagram(pdf, x, accent):
    values = ("8", "5", "9", "3", "7")
    for i, value in enumerate(values):
        bx = x + 20 + i * 47
        selected = 1 <= i <= 3
        pdf.setFillColor(colors.HexColor("#DBEAFE") if selected else PALE)
        pdf.setStrokeColor(accent if selected else BORDER)
        pdf.roundRect(bx, 268, 40, 38, 5, stroke=1, fill=1)
        pdf.setFillColor(INK)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(bx + 20, 282, value)
    pdf.setStrokeColor(accent)
    pdf.setLineWidth(2)
    pdf.line(x + 70, 252, x + 205, 252)
    pdf.setFillColor(accent)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(x + 140, 234, "inspect each selected value")


def draw_sparse_diagram(pdf, x, accent):
    for row, y in enumerate((302, 274, 246)):
        count = 5 - row
        for i in range(count):
            bx = x + 25 + i * (46 * (row + 1))
            box_width = 40 * (row + 1)
            pdf.setFillColor(colors.HexColor("#FFEDD5"))
            pdf.setStrokeColor(accent)
            pdf.roundRect(bx, y, box_width, 20, 3, stroke=1, fill=1)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(x + 140, 224, "precomputed overlapping blocks")


def draw_tree_diagram(pdf, x, accent):
    coords = [(140, 307), (92, 267), (188, 267), (68, 229),
              (116, 229), (164, 229), (212, 229)]
    for left, right in ((0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)):
        pdf.setStrokeColor(accent)
        pdf.setLineWidth(1.4)
        pdf.line(x + coords[left][0], coords[left][1] - 8,
                 x + coords[right][0], coords[right][1] + 8)
    for i, (cx, cy) in enumerate(coords):
        pdf.setFillColor(colors.HexColor("#DCFCE7"))
        pdf.setStrokeColor(accent)
        pdf.circle(x + cx, cy, 12 if i < 3 else 9, stroke=1, fill=1)
        if i < 3:
            pdf.setFillColor(INK)
            pdf.setFont("Helvetica-Bold", 8)
            pdf.drawCentredString(x + cx, cy - 3, "min")
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(x + 140, 211, "recompute only one tree path")


def draw_approaches(pdf):
    draw_base(pdf, 2, "The approaches", "Three ways to find the minimum")
    items = (
        (54, BLUE, "1. Linear scan", "Check each value in the requested range.",
         "Query O(n)  |  Update O(1)",
         "Best for tiny arrays and simple reference implementations.", draw_scan_diagram),
        (340, ORANGE, "2. Sparse table",
         "Precompute interval minimums; combine two blocks per query.",
         "Query O(1)  |  Update O(n log n)*",
         "Best for static data with many range queries.", draw_sparse_diagram),
        (626, GREEN, "3. Segment tree",
         "Store interval minimums; update one path in the tree.",
         "Query O(log n)  |  Update O(log n)",
         "Best when queries and point updates both matter.", draw_tree_diagram),
    )
    for x, accent, title, description, complexity, best, draw_diagram in items:
        draw_card(pdf, x, 140, 280, 298, accent)
        pdf.setFillColor(INK)
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(x + 18, 405, title)
        draw_paragraph(pdf, description, x + 18, 382, 242, 12, 17, MUTED)
        draw_diagram(pdf, x, accent)
        pdf.setFillColor(accent)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(x + 18, 191, complexity)
        draw_paragraph(pdf, best, x + 18, 177, 244, 10.5, 14, INK)

    draw_card(pdf, 54, 73, 852, 54, ORANGE, colors.HexColor("#FFF7ED"))
    draw_paragraph(pdf,
        "<b>Memory:</b> linear scan and segment tree use O(n); sparse table "
        "uses O(n log n).  <font color='#9A3412'>*This implementation "
        "rebuilds the sparse table after an update.</font>",
        72, 120, 815, 11, 15, INK,
    )
    pdf.showPage()


def draw_benchmark(pdf):
    draw_base(pdf, 3, "Experimental evidence",
              "Query speed versus update cost")
    draw_card(pdf, 54, 155, 405, 277, BLUE)
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(74, 402, "Average operation time")
    headers = ("n", "Linear query", "Sparse query", "Tree query")
    rows = (
        ("1,000", "12.163 µs", "0.283 µs", "1.329 µs"),
        ("10,000", "128.625 µs", "0.312 µs", "1.943 µs"),
        ("30,000", "422.677 µs", "0.345 µs", "3.711 µs"),
    )
    columns = (74, 142, 245, 348)
    for index, header in enumerate(headers):
        pdf.setFillColor(BLUE if index else NAVY)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(columns[index], 369, header)
    pdf.setStrokeColor(BORDER)
    pdf.line(74, 361, 438, 361)
    for row_index, row in enumerate(rows):
        y = 335 - row_index * 34
        for column_index, value in enumerate(row):
            pdf.setFillColor(INK)
            pdf.setFont("Helvetica-Bold" if column_index == 0 else "Helvetica", 9)
            pdf.drawString(columns[column_index], y, value)
        pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
        pdf.line(74, y - 8, 438, y - 8)

    draw_paragraph(pdf,
        "<b>At n = 30,000</b><br/>Sparse-table update: 70.728 ms"
        "<br/>Segment-tree update: 2.996 µs",
        74, 249, 360, 12, 18, INK,
    )
    draw_paragraph(pdf,
        "The sparse table has the fastest queries, but rebuilding it makes "
        "updates expensive. The segment tree keeps both operations fast.",
        74, 190, 360, 10.5, 14, MUTED,
    )

    draw_card(pdf, 476, 155, 430, 277, GREEN)
    chart = ROOT / "results" / "benchmark_chart.png"
    pdf.drawImage(ImageReader(str(chart)), 492, 180, width=397, height=240,
                  preserveAspectRatio=True, anchor="c", mask="auto")

    draw_card(pdf, 54, 86, 852, 57, GREEN, colors.HexColor("#F0FDF4"))
    draw_paragraph(pdf,
        "<b>Conclusion:</b> for changing scores, the segment tree is the best "
        "overall balance of query time, update time, and memory.",
        73, 123, 812, 12, 17, INK,
    )
    pdf.showPage()


def draw_conclusion(pdf):
    draw_base(pdf, 4, "Conclusion and validation",
              "Use a segment tree for changing data")

    draw_card(pdf, 54, 265, 405, 165, GREEN, colors.HexColor("#F0FDF4"))
    draw_paragraph(pdf, "Recommended structure", 76, 398, 360, 11, 14, GREEN, bold=True)
    draw_paragraph(pdf, "Segment tree", 76, 370, 360, 25, 30, NAVY, bold=True)
    draw_bullet(pdf, "Query and update: O(log n)", 78, 330, 350, 12)
    draw_bullet(pdf, "Storage: O(n)", 78, 299, 350, 12)

    draw_card(pdf, 476, 265, 430, 165, BLUE)
    draw_paragraph(pdf, "Choose by workload", 498, 398, 380, 11, 14, BLUE, bold=True)
    draw_bullet(pdf, "<b>Sparse table:</b> static data, query-heavy workloads.",
                500, 367, 380, 11)
    draw_bullet(pdf, "<b>Linear scan:</b> tiny data or very few queries.",
                500, 331, 380, 11)
    draw_bullet(pdf, "<b>Segment tree:</b> changing data and frequent queries.",
                500, 295, 380, 11)

    draw_card(pdf, 54, 105, 852, 145, ORANGE, colors.HexColor("#FFF7ED"))
    draw_paragraph(pdf, "Correctness checks", 76, 226, 800, 14, 18, ORANGE, bold=True)
    checks = (
        "Hand-worked and full-range queries, single-element and boundary ranges.",
        "First/last-index updates; negative values, duplicates, and non-power-of-two lengths.",
        "Invalid input handling and deterministic randomized operations against a direct reference.",
    )
    y = 194
    for check in checks:
        y = draw_bullet(pdf, check, 78, y, 790, 11) - 7
    draw_paragraph(pdf,
        "<b>All 7 test methods pass for all three implementations.</b> "
        "The benchmark verifies query answers before timing.",
        76, 125, 790, 11, 15, INK,
    )
    draw_paragraph(pdf,
        "Full report: docs/report.pdf  ·  DOCX: docs/report.docx  ·  "
        "Code, CSV, graph, and tests are linked in the project README.",
        58, 78, 840, 9, 12, MUTED,
    )
def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=(WIDTH, HEIGHT), pageCompression=1)
    pdf.setTitle("Range Minimum Query with Point Updates — Case Study 02")
    pdf.setAuthor(
        "Daksh Srivastava; Prathamesh More; Yuvraj Mishra; "
        "Biswajeet Rout; Sumit Shingole"
    )
    draw_cover(pdf)
    draw_approaches(pdf)
    draw_benchmark(pdf)
    draw_conclusion(pdf)
    pdf.save()
    print("Created {}".format(OUTPUT))


if __name__ == "__main__":
    main()
