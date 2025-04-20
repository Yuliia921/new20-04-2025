
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from generate_pdf import generate_pdf
import uuid
import smtplib
from email.message import EmailMessage
import os
from fpdf import FPDF

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/fonts", StaticFiles(directory="fonts"), name="fonts")

app.post("/generate_pdf")(generate_pdf)

@app.get("/")
def root():
    return FileResponse("static/pregnancy.html")

@app.get("/consultation")
def consultation():
    return FileResponse("static/consultation.html")

@app.get("/consultation_form")
def consultation_form():
    return FileResponse("static/consultation_form.html")

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
    pdf.cell(0, 10, "💬 Консультативное заключение", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 10, f"Дата: {date}")
    pdf.multi_cell(0, 10, f"ФИО: {fio}")
    pdf.multi_cell(0, 10, f"Возраст: {age}")
    pdf.multi_cell(0, 10, f"Диагноз: {diagnosis}")
    pdf.multi_cell(0, 10, f"Обследование: {examination}")
    pdf.multi_cell(0, 10, f"Рекомендации: {recommendations}")

    pdf.ln(10)
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 10, "врач акушер-гинеколог Куриленко Юлия Сергеевна", ln=True)
    pdf.cell(0, 10, "Телефон: +374 55 98 77 15", ln=True)
    pdf.cell(0, 10, "Telegram: t.me/ginekolog_doc_bot", ln=True)

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
