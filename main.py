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
    return text.strip().replace("🌸", "").replace("💬", "").replace("📤", "")

@app.get("/", response_class=HTMLResponse)
async def serve_ultrasound(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/pelvis", response_class=HTMLResponse)
async def serve_pelvis(request: Request):
    return templates.TemplateResponse("pelvis.html", {"request": request})

@app.get("/consultation", response_class=HTMLResponse)
async def serve_consultation(request: Request):
    return templates.TemplateResponse("consultation.html", {"request": request})

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
    mecho: str = Form(""),
    myometrium: str = Form(""),
    cervix: str = Form(""),
    right_ovary: str = Form(""),
    left_ovary: str = Form(""),
    fluid: str = Form("")

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
    pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)

    is_ultrasound = any([lmp.strip(), crl.strip(), gestationalSac.strip()])

    pdf.set_font("DejaVu", "B", 16)
    title = "УЗИ малого таза (беременность)" if is_ultrasound else "Консультативное заключение"
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("DejaVu", "", 12)

    
    if all([uterus.strip(), mecho.strip(), right_ovary.strip(), left_ovary.strip()]):
        is_pelvis = True
    else:
        is_pelvis = False

    if is_pelvis:
        fields_ultrasound = [
            ("ФИО", f"{clean_value(fio)}\nВозраст: {clean_value(age)}"),
            ("Последняя менструация", lmp),
            ("Описание матки", uterus),
            ("Структура миометрия", myometrium),
            ("М-эхо", mecho),
            ("Шейка матки", cervix),
            ("Правый яичник", right_ovary),
            ("Левый яичник", left_ovary),
            ("Дополнительные образования", additional),
            ("Свободная жидкость", fluid),
            ("Заключение", conclusion),
            ("Рекомендации", recommendations)
        ]
    else:
        fields_ultrasound = [("ФИО", f"{clean_value(fio)}\nВозраст: {clean_value(age)}"),

        ("Последняя менструация", lmp),
        ("Плодное яйцо (мм)", gestationalSac),
        ("КТР (мм)", crl),
        ("Срок (нед)", term),
        ("Желточный мешок (мм)", yolkSac),
        ("Сердцебиение", heartbeat),
        ("ЧСС (уд/мин)", hr),
        ("Хорион", chorion),
        ("Желтое тело", corpusLuteum),
        ("Дополнительно", additional),
        ("Заключение", conclusion),
        ("Рекомендации", recommendations),
    ]

    fields_consultation = [("ФИО", f"{clean_value(fio)}\nВозраст: {clean_value(age)}"), ("Диагноз", diagnosis), ("Обследование", examination), ("Рекомендации", recommendations)]

    fields = fields_ultrasound if is_ultrasound else fields_consultation

    for label, value in fields:
        text_line = f"{label.strip()}: {clean_value(value)}"
        try:
            pdf.multi_cell(180, 10, text_line)
        except:
            pdf.multi_cell(180, 10, f"{label.strip()}: -")
        pdf.ln(1)

    pdf.ln(12)
    pdf.set_font("DejaVu", "", 9)
    pdf.cell(0, 6, "врач акушер-гинеколог Куриленко Юлия Сергеевна", ln=True)
    pdf.cell(0, 6, "Телефон: +37455987715", ln=True)
    pdf.cell(0, 6, "Telegram: https://t.me/doc_Kurilenko", ln=True)

    filename = f"/tmp/protocol_{uuid4().hex}.pdf"
    pdf.output(filename)

    if email.strip():
        try:
            smtp_user = os.getenv("SMTP_USER")
            smtp_pass = os.getenv("SMTP_PASS")

            msg = EmailMessage()
            msg["Subject"] = "Ваш протокол из Док Куриленко"
            msg["From"] = smtp_user
            msg["To"] = email.strip()
            msg.set_content("Здравствуйте! Во вложении — ваш протокол в формате PDF.\n\nС уважением,\nКуриленко Ю.С.")

            with open(filename, "rb") as f:
                msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="protocol.pdf")

            with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as smtp:
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg)

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Ошибка отправки письма: {str(e)}"})

    return FileResponse(filename, media_type="application/pdf", filename="protocol.pdf")
