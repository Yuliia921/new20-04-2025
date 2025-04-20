
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fpdf import FPDF
import uuid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def remove_non_latin1(text):
    return ''.join(c for c in text if ord(c) < 256)

@app.get("/")
def root():
    return FileResponse("static/pregnancy.html")

@app.get("/consultation")
def consultation():
    return FileResponse("static/consultation.html")

@app.post("/generate_pdf")
async def generate_pdf(
    fio: str = Form(...),
    lmp: str = Form(...),
    uterus: str = Form(...),
    gestationalSac: str = Form(...),
    crl: str = Form(...),
    term: str = Form(...),
    yolkSac: str = Form(...),
    heartbeat: str = Form(...),
    hr: str = Form(...),
    chorion: str = Form(...),
    corpusLuteum: str = Form(...),
    additional: str = Form(...),
    conclusion: str = Form(...),
    recommendations: str = Form(...)
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, "УЗИ малого таза (беременность)", ln=True, align="C")
    pdf.ln(10)

    fields = [
        ("ФИО", fio),
        ("Последняя менструация", lmp),
        ("Матка", uterus),
        ("Плодное яйцо", gestationalSac),
        ("КТР", crl),
        ("Срок", term),
        ("Желточный мешок", yolkSac),
        ("Сердцебиение", heartbeat),
        ("ЧСС", hr),
        ("Хорион", chorion),
        ("Желтое тело", corpusLuteum),
        ("Дополнительно", additional),
        ("Заключение", conclusion),
        ("Рекомендации", recommendations)
    ]

    for label, value in fields:
        clean_value = remove_non_latin1(value)
        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 10, f"{label}: {clean_value}")

    pdf.ln(10)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 10, "врач акушер-гинеколог Куриленко Юлия Сергеевна", ln=True)
    pdf.cell(0, 10, "Телефон: +374 55 98 77 15", ln=True)
    pdf.cell(0, 10, "Telegram: t.me/ginekolog_doc_bot", ln=True)

    filename = f"/mnt/data/protocol_{uuid.uuid4().hex}.pdf"
    pdf.output(filename)
    return FileResponse(filename, media_type="application/pdf", filename="protocol.pdf")
