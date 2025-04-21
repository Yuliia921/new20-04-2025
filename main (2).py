
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fpdf import FPDF
import uuid
import os

app = FastAPI()

def clean(text):
    try:
        return str(text).replace("\n", " ").replace("\r", " ").strip()
    except:
        return "-"

@app.post("/generate_pdf")
async def generate_pdf(request: Request):
    data = await request.form()
    filename = f"/mnt/data/protocol_{uuid.uuid4().hex}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=14)

    for label, value in data.items():
        try:
            pdf.multi_cell(180, 10, clean(f"{label}: {value}"))
        except:
            pdf.multi_cell(180, 10, "-")

    os.makedirs("/mnt/data", exist_ok=True)
    pdf.output(filename)

    return FileResponse(filename, media_type="application/pdf", filename="protocol.pdf")
