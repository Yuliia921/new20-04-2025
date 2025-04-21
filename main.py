from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fpdf import FPDF
import uuid

app = FastAPI()

@app.post("/generate_pdf")
async def generate_pdf(request: Request):
    data = await request.form()
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "./DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)

    def clean(text):
        if not text or text.strip() == "":
            return "-"
        return text.replace("🌸", "-")

    for label, value in data.items():
        try:
            pdf.multi_cell(0, 10, clean(f"{label}: {value}"))
        except Exception:
            pdf.multi_cell(0, 10, "-")

    filename = f"/mnt/data/protocol_{uuid.uuid4().hex}.pdf"
    pdf.output(filename)

    return FileResponse(filename, media_type="application/pdf", filename="protocol.pdf")