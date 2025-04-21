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

def clean_value(text):
    if not text or text.strip() == "":
        return "-"
    try:
        return text.replace("🌸", "").replace("💬", "").replace("📤", "").strip()
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
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)

    # Определение шаблона
    is_ultrasound = any([lmp.strip(), crl.strip(), gestationalSac.strip()])

    # Заголовок
    pdf.set_font("DejaVu", "B", 16)
    title = "УЗИ малого таза (беременность)" if is_ultrasound else "Консультативное заключение"
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("DejaVu", "", 12)

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
            ("Заключение", conclusion),
            ("Рекомендации", recommendations),
        ]

    for label, value in fields:
        if not label:
            continue
        safe_value = clean_value(value)
        text_line = f"{label.strip()}: {safe_value or '-'}"
        if len(text_line.strip()) < 3:
            text_line = f"{label.strip()}: -"
        try:
            pdf.multi_cell(180, 10, text_line)
        except:
            pdf.multi_cell(180, 10, f"{label.strip()}: -")
        pdf.ln(1)

    # Подпись и контакты — с отступом и уменьшенным шрифтом
    pdf.ln(12)
    pdf.set_font("DejaVu", "", 9)
    pdf.multi_cell(180, 6, "врач акушер-гинеколог Куриленко Юлия Сергеевна")
    pdf.multi_cell(180, 6, "Телефон: +37455987715")
    pdf.multi_cell(180, 6, "Telegram: https://t.me/doc_Kurilenko")

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