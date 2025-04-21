import os
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fpdf import FPDF
from uuid import uuid4

app = FastAPI()

# Разрешённая директория на Render
os.makedirs("/tmp", exist_ok=True)

def clean(text):
    try:
        return text.encode("latin1").decode("latin1")
    except UnicodeEncodeError:
        return "-"

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
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "УЗИ малого таза (беременность)", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("DejaVu", "", 12)

    fields = [
        ("ФИО пациентки", fio),
        ("Последняя менструация", lmp),
        ("Положение и форма матки", uterus),
        ("Плодное яйцо (мм)", gestationalSac),
        ("КТР (мм)", crl),
        ("Срок (нед)", term),
        ("Желточный мешок (мм)", yolkSac),
        ("Сердцебиение", heartbeat),
        ("ЧСС (уд/мин)", hr),
        ("Расположение хориона", chorion),
        ("Желтое тело", corpusLuteum),
        ("Дополнительные данные", additional),
        ("Заключение", conclusion),
        ("Рекомендации", recommendations),
    ]

    for label, value in fields:
        try:
            pdf.multi_cell(0, 10, clean(f"{label}: {value or '-'}"))
        except:
            pdf.multi_cell(0, 10, f"{label}: -")

    pdf.ln(5)
    pdf.set_font("DejaVu", "", 10)
    pdf.multi_cell(0, 8, "врач акушер-гинеколог Куриленко Юлия Сергеевна")

    filename = f"/tmp/protocol_{uuid4().hex}.pdf"
    pdf.output(filename)
    return FileResponse(filename, media_type="application/pdf", filename="protocol.pdf")
