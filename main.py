
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Статическая директория для PDF
PDF_DIRECTORY = "static/protocols"
os.makedirs(PDF_DIRECTORY, exist_ok=True)

@app.get("/view/{protocol_id}", response_class=HTMLResponse)
async def view_protocol(protocol_id: int):
    file_path = f"{PDF_DIRECTORY}/{protocol_id}.pdf"
    if os.path.exists(file_path):
        return f'''<html><body><embed src="/{file_path}" width="100%" height="1000px" /></body></html>'''
    else:
        return HTMLResponse(content="Файл не найден", status_code=404)

# Пример генерации PDF с датой (упрощённая версия)
@app.post("/generate_pdf")
async def generate_pdf(fio: str = Form(...), content: str = Form(...)):
    from fpdf import FPDF
    pdf_path = f"{PDF_DIRECTORY}/test.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", "", 14)
    pdf.multi_cell(0, 10, f"ФИО: {fio}")
    pdf.multi_cell(0, 10, f"Содержимое: {content}")
    pdf.multi_cell(0, 10, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")

    pdf.output(pdf_path)
    return FileResponse(pdf_path, media_type='application/pdf', filename="generated.pdf")
