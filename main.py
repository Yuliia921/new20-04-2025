
from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from fpdf import FPDF
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/generate_pdf")
async def generate_pdf(request: Request):
    form = await request.form()
    data = dict(form)

    class PDF(FPDF):
        def header(self):
            self.set_font("DejaVu", "B", 14)
            self.cell(0, 10, "Протокол УЗИ", ln=True, align="C")
            self.ln(10)

    pdf = PDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)

    def clean(text):
        try:
            return str(text)
        except Exception:
            return "-"

    for label, value in data.items():
        try:
            pdf.multi_cell(0, 10, clean(f"{label}: {value or '-'}"))
        except Exception:
            pdf.multi_cell(0, 10, "-")

    pdf.ln(10)
    pdf.set_font("DejaVu", size=10)
    pdf.multi_cell(0, 8, "врач акушер-гинеколог Куриленко Юлия Сергеевна
+37455987715
https://t.me/ginekolog_doc_bot")

    filename = f"/mnt/data/protocol_{uuid4().hex}.pdf"
    os.makedirs("/mnt/data", exist_ok=True)
    pdf.output(filename)
    return FileResponse(filename, media_type="application/pdf", filename="protocol.pdf")
