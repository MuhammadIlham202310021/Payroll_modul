from xml.sax.saxutils import escape

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

styles = getSampleStyleSheet()
TITLE = ParagraphStyle('TitleX', parent=styles['Title'], fontSize=16, spaceAfter=6)
INFO = ParagraphStyle('InfoX', parent=styles['Normal'], fontSize=9, leading=12)
HEADING = ParagraphStyle('HeadingX', parent=styles['Heading2'], fontSize=12, spaceBefore=14, spaceAfter=6)
CELL = ParagraphStyle('CellX', parent=styles['Normal'], fontSize=8, leading=10)
CELL_HEAD = ParagraphStyle('CellHeadX', parent=CELL, textColor=colors.white, fontName='Helvetica-Bold')
CELL_BOLD = ParagraphStyle('CellBoldX', parent=CELL, fontName='Helvetica-Bold')

DARK = colors.HexColor('#212529')
GREY = colors.HexColor('#E9ECEF')
LINE = colors.HexColor('#BBBBBB')


def _p(text, style=CELL):
    return Paragraph(escape(str(text)), style)


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.grey)
    width, _ = landscape(A4)
    canvas.drawString(1.5 * cm, 1 * cm, 'Report Biodata')
    canvas.drawRightString(width - 1.5 * cm, 1 * cm, f'Halaman {doc.page}')
    canvas.restoreState()


def _table_data(qs):
    headers = ['No', 'EMP Code', 'EMP Name', 'ID Card', 'Sex', 'Birth Place',
               'Birth Date', 'Company Begin', 'Department', 'Division']
    widths = [1.0, 2.2, 4.4, 3.4, 1.6, 2.8, 2.2, 2.3, 2.9, 3.6]

    rows = [[_p(h, CELL_HEAD) for h in headers]]
    for no, p in enumerate(qs, start=1):
        rows.append([
            _p(no),
            _p(p.emp_code),
            _p(p.emp_name),
            _p(p.id_card),
            _p(p.get_sex_display()),
            _p(p.birth_place),
            _p(p.birth_date.strftime('%d-%m-%Y')),
            _p(p.company_begin.strftime('%d-%m-%Y')),
            _p(p.division.department.department_name),
            _p(p.division.division_name),
        ])

    table = Table(rows, colWidths=[w * cm for w in widths], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK),
        ('GRID', (0, 0), (-1, -1), 0.4, LINE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return table

# menyusun ringkasan dari build_summary yang sama dengan halaman Report dan Excel
def _summary_table(summary):
    rows = [[_p('Department / Division', CELL_HEAD), _p('Jumlah', CELL_HEAD)]]
    dept_rows = []
    grand_total = 0

    for d in summary:
        rows.append([_p(f"{d['code']} - {d['name']}", CELL_BOLD), _p(d['total'], CELL_BOLD)])
        dept_rows.append(len(rows) - 1)
        grand_total += d['total']
        for v in d['divisions']:
            rows.append([_p(f"      {v['code']} - {v['name']}"), _p(v['total'])])

    rows.append([_p('TOTAL', CELL_BOLD), _p(grand_total, CELL_BOLD)])

    table = Table(rows, colWidths=[10 * cm, 3 * cm], hAlign='LEFT', repeatRows=1)
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), DARK),
        ('GRID', (0, 0), (-1, -1), 0.4, LINE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, -1), (-1, -1), GREY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]
    for r in dept_rows:
        style.append(('BACKGROUND', (0, r), (-1, r), GREY))
    table.setStyle(TableStyle(style))
    return table


def build_pdf(target, qs, summary, label, username):
    doc = SimpleDocTemplate(
        target,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.8 * cm,
        title='Report Biodata',
    )

    now = timezone.localtime()
    story = [
        Paragraph('REPORT BIODATA', TITLE),
        Paragraph(f'<b>Filter:</b> {escape(label)}', INFO),
        Paragraph(f'<b>Tanggal cetak:</b> {now:%d-%m-%Y %H:%M}', INFO),
        Paragraph(f'<b>Dicetak oleh:</b> {escape(username)}', INFO),
        Spacer(1, 10),
        _table_data(qs),
        KeepTogether([
            Paragraph('Ringkasan Jumlah Pekerja', HEADING),
            _summary_table(summary),
        ]),
    ]

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)