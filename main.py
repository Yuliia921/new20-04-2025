import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from email.message import EmailMessage
import smtplib
from uuid import uuid4
from fpdf import FPDF

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
os.makedirs("/tmp", exist_ok=True)

def clean(text):
    if not text or text.strip() == "":
        return "-"
    try:
        text = text.replace("🌸", "").replace("💬", "").replace("📤", "")
        return text.encode("latin1", "ignore").decode("latin1")
    except:
        return "-"

@app.get("/", response_class=HTMLResponse)
async def serve_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate_pdf")
async def generate_pdf(
    request: Request,
    fio: str = Form(""),
    email: str = Form(""),
    lmp: str = Form(""),
    uterus: str = Form(""),
    gestationalSac: str = Form(""),
    crl: str = Form(""),
    term: str = Form(""),
    yolkSac: str = Form(""),
    heartbeat: str = Form(""),
    hr: str = Form(""),
    chorion: str = Form(""),
    corpusLuteum: str = Form(""),
    additional: str = Form(""),
    conclusion: str = Form(""),
    age: str = Form(""),
    diagnosis: str = Form(""),
    examination: str = Form(""),
    recommendations: str = Form(""),
):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)

    # Заголовок
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Протокол приёма", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("DejaVu", "", 12)

    # Определение типа шаблона
    is_ultrasound = any([lmp.strip(), crl.strip(), gestationalSac.strip()])
    if is_ultrasound:
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
    else:
        fields = [
            ("ФИО", fio),
            ("Возраст", age),
            ("Диагноз", diagnosis),
            ("Обследование", examination),
            ("Рекомендации", recommendations),
        ]

    for label, value in fields:
        try:
            line = clean(f"{label}: {value or '-'}")
            if len(line.strip()) < 2:
                line += " ."
            pdf.multi_cell(190, 10, line)
        except:
            pdf.multi_cell(190, 10, f"{label}: -")

    # Контактная информация
    pdf.ln(10)
    pdf.set_font("DejaVu", "", 11)
    pdf.multi_cell(190, 8, "врач акушер-гинеколог Куриленко Юлия Сергеевна")
    pdf.multi_cell(190, 8, "Телефон: +37455987715")
    pdf.multi_cell(190, 8, "Telegram: https://t.me/doc_Kurilenko")

    filename = f"/tmp/protocol_{uuid4().hex}.pdf"
    pdf.output(filename)

    try:
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")

        msg = EmailMessage()
        msg["Subject"] = "Ваш протокол из Док Куриленко"
        msg["From"] = smtp_user
        msg["To"] = email.strip()
        msg.set_content("Здравствуйте! Во вложении — ваш протокол в формате PDF.\n\nС уважением,\nКуриленко Ю.С.")

        with open(filename, "rb") as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype="application", subtype="pdf", filename="protocol.pdf")

        with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Ошибка отправки письма: {str(e)}"})

    return FileResponse(filename, media_type="application/pdf", filename="protocol.pdf")
