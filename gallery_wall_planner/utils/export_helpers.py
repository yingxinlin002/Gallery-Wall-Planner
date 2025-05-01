import openpyxl
from openpyxl.styles import Font
from docx import Document
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas


def save_to_excel(lines, filename):
    """
    Save a list of instruction lines to an Excel (.xlsx) file.

    Args:
        lines (list of str): The lines to save.
        filename (str): The output Excel file path.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Instructions"

    bold_font = Font(bold=True)

    for idx, line in enumerate(lines, start=1):
        cell = ws.cell(row=idx, column=1, value=line)
        cell.font = bold_font if idx == 1 else None

    wb.save(filename)


def save_to_text(lines, filename):
    """
    Save a list of instruction lines to a plain text (.txt) file.

    Args:
        lines (list of str): The lines to save.
        filename (str): The output text file path.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def save_to_word(lines, filename):
    """
    Save a list of instruction lines to a Microsoft Word (.docx) file.

    Args:
        lines (list of str): The lines to save.
        filename (str): The output Word file path.
    """
    doc = Document()
    for line in lines:
        doc.add_paragraph(line)
    doc.save(filename)


def save_to_pdf(lines, filename):
    """
    Save a list of instruction lines to a PDF (.pdf) file.

    Args:
        lines (list of str): The lines to save.
        filename (str): The output PDF file path.
    """
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 40

    for line in lines:
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line)
        y -= 20

    c.save()
