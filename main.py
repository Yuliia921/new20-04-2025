
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fpdf import FPDF
import uuid
import smtplib
from email.message import EmailMessage
import os

def clean(text):
    return (text or '-').encode('latin-1', 'replace').decode('latin-1')

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/fonts", StaticFiles(directory="fonts"), name="fonts")

@app.get("/")
def root():
    return FileResponse("static/pregnancy.html")

@app.get("/consultation_form")
def consultation_form():
    return FileResponse("static/consultation_form.html")

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
    pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", "", 14)
    pdf.cell(0, 10, clean("УЗИ малого таза (беременность)"), ln=True, align="C")
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

    pdf.set_font("DejaVu", "", 12)
    for label, value in fields:
        pdf.multi_cell(0, 10, clean(f"{label}: {value}"))

    pdf.ln(10)
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 10, clean("врач акушер-гинеколог Куриленко Юлия Сергеевна"), ln=True)
    pdf.cell(0, 10, clean("Телефон: +374 55 98 77 15"), ln=True)
    pdf.cell(0, 10, clean("Telegram: t.me/ginekolog_doc_bot"), ln=True)

    filename = f"/mnt/data/protocol_{uuid.uuid4().hex}.pdf"
    pdf.output(filename)
    return FileResponse(filename, media_type="application/pdf", filename="protocol.pdf")

@app.post("/generate_consultation")
async def generate_consultation(
    date: str = Form(...),
    fio: str = Form(...),
    age: str = Form(...),
    diagnosis: str = Form(...),
    examination: str = Form(...),
    recommendations: str = Form(...)
):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", "", 14)
    pdf.cell(0, 10, clean("Консультативное заключение"), ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 10, clean(f"Дата: {date}"))
    pdf.multi_cell(0, 10, clean(f"ФИО: {fio}"))
    pdf.multi_cell(0, 10, clean(f"Возраст: {age}"))
    pdf.multi_cell(0, 10, clean(f"Диагноз: {diagnosis}"))
    pdf.multi_cell(0, 10, clean(f"Обследование: {examination}"))
    pdf.multi_cell(0, 10, clean(f"Рекомендации: {recommendations}"))

    pdf.ln(10)
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 10, clean("врач акушер-гинеколог Куриленко Юлия Сергеевна"), ln=True)
    pdf.cell(0, 10, clean("Телефон: +374 55 98 77 15"), ln=True)
    pdf.cell(0, 10, clean("Telegram: t.me/ginekolog_doc_bot"), ln=True)

    filename = f"/mnt/data/consultation_{uuid.uuid4().hex}.pdf"
    pdf.output(filename)
    return FileResponse(filename, media_type="application/pdf", filename="consultation.pdf")

@app.post("/send_email")
async def send_email(email: str = Form(...), file: UploadFile = File(...)):
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    msg = EmailMessage()
    msg["Subject"] = "Ваш протокол из Док Куриленко"
    msg["From"] = smtp_user
    msg["To"] = email
    msg.set_content("Здравствуйте! Во вложении — ваш протокол в формате PDF.\n\nС уважением,\nКуриленко Ю.С.")

    content = await file.read()
    msg.add_attachment(content, maintype="application", subtype="pdf", filename=file.filename)

    with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)

    return {"message": "Письмо отправлено!"}
