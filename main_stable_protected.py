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
    fio: str = Form(...),
    email: str = Form(...),
    lmp: str = Form(None),
    uterus: str = Form(None),
    gestationalSac: str = Form(None),
    crl: str = Form(None),
    term: str = Form(None),
    yolkSac: str = Form(None),
    heartbeat: str = Form(None),
    hr: str = Form(None),
    chorion: str = Form(None),
    corpusLuteum: str = Form(None),
    additional: str = Form(None),
    conclusion: str = Form(None),
    age: str = Form(None),
    diagnosis: str = Form(None),
    examination: str = Form(None),
    recommendations: str = Form(None),
):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Протокол приёма", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("DejaVu", "", 12)

    fields = []

    if lmp or crl or gestationalSac:
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
            safe_text = clean(f"{label}: {value or '-'}")
            if len(safe_text.strip()) < 2:
                safe_text += " ."
            pdf.multi_cell(190, 10, safe_text)
        except:
            pdf.multi_cell(190, 10, f"{label}: -")

    pdf.ln(5)
    pdf.set_font("DejaVu", "", 10)
    pdf.multi_cell(190, 8, "врач акушер-гинеколог Куриленко Юлия Сергеевна")

    filename = f"/tmp/protocol_{uuid4().hex}.pdf"
    pdf.output(filename)

    try:
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")

        msg = EmailMessage()
        msg["Subject"] = "Ваш протокол из Док Куриленко"
        msg["From"] = smtp_user
        msg["To"] = email
        msg.set_content("Здравствуйте! Во вложении — ваш протокол в формате PDF.\n\nС уважением,\nКуриленко Ю.С.")

        with open(filename, "rb") as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype="application", subtype="pdf", filename="protocol.pdf")

        with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    return FileResponse(filename, media_type="application/pdf", filename="protocol.pdf")