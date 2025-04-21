
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fpdf import FPDF
import uuid
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def clean(text):
    try:
        return text.replace("\n", " ").strip()
    except:
        return "-"

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("pregnancy.html", encoding="utf-8") as f:
        return f.read()

@app.get("/consultation", response_class=HTMLResponse)
async def consultation_page():
    with open("consultation.html", encoding="utf-8") as f:
        return f.read()

@app.post("/generate_pdf")
async def generate_pdf(request: Request):
    data = await request.form()
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "🌸 УЗИ малого таза (беременность)", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("DejaVu", "", 14)

    for label, value in data.items():
        try:
            pdf.multi_cell(0, 10, clean(f"{label}: {value or '-'}"))
        except:
            pdf.multi_cell(0, 10, "-")

    pdf.ln(5)
    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 8, "Врач акушер-гинеколог Куриленко Юлия Сергеевна")
    pdf.multi_cell(0, 8, "Тел.: +37455987715")
    pdf.multi_cell(0, 8, "tg: @ginekolog_doc_bot")

    filename = f"/mnt/data/protocol_{uuid.uuid4().hex}.pdf"
    pdf.output(filename)
    return FileResponse(filename, media_type="application/pdf", filename="protocol.pdf")
