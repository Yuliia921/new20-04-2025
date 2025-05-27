
import os
import sqlite3
from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from email.message import EmailMessage
import smtplib
from uuid import uuid4
from fpdf import FPDF
from datetime import datetime

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS protocols (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fio TEXT NOT NULL,
        date TEXT NOT NULL,
        template TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
os.makedirs("/tmp", exist_ok=True)

DB_PATH = "data/database.db"

def save_to_db(fio, template, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO protocols (fio, date, template, content) VALUES (?, ?, ?, ?)",
                   (fio.strip(), date, template, content))
    conn.commit()
    conn.close()

def clean_value(text):
    if not text or text.strip() == "":
        return "-"
    return text.strip().replace("🌸", "").replace("💬", "").replace("📤", "")

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/uzib", response_class=HTMLResponse)
async def serve_uzib(request: Request):
    return templates.TemplateResponse("uzib.html", {"request": request})

@app.get("/pelvis", response_class=HTMLResponse)
async def serve_pelvis(request: Request):
    return templates.TemplateResponse("pelvis.html", {"request": request})

@app.get("/consultation", response_class=HTMLResponse)
async def serve_consultation(request: Request):
    return templates.TemplateResponse("consultation.html", {"request": request})

@app.get("/primary", response_class=HTMLResponse)
async def serve_primary(request: Request):
    return templates.TemplateResponse("primary.html", {"request": request})

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
    complaints: str = Form(""),
    mecho: str = Form(""),
    myometrium: str = Form(""),
    cervix: str = Form(""),
    right_ovary: str = Form(""),
    left_ovary: str = Form(""),
    fluid: str = Form(""),
    birthdate: str = Form(""),
    anamnez_morbi: str = Form(""),
    gyn_anamnez: str = Form(""),
    menarche: str = Form(""),
    menstruation: str = Form(""),
    last_period: str = Form(""),
    pregnancies: str = Form(""),
    gyn_diseases: str = Form(""),
    somatic_diseases: str = Form(""),
    objective: str = Form(""),
    breasts: str = Form(""),
    abdomen: str = Form(""),
    diuresis: str = Form(""),
    stool: str = Form(""),
    external_genitals: str = Form(""),
    speculum: str = Form(""),
    discharge: str = Form(""),
    pv: str = Form("")
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)

    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Протокол", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("DejaVu", "", 12)

    is_ultrasound = any([crl.strip(), gestationalSac.strip(), chorion.strip()])
    is_pelvis = any([mecho.strip(), myometrium.strip(), right_ovary.strip(), left_ovary.strip(), fluid.strip()])

    if is_ultrasound:
        title = "УЗИ малого таза (беременность)"
        fields = [("ФИО", f"{clean_value(fio)}\nВозраст: {clean_value(age)}"),
                  ("Последняя менструация", lmp), ("Плодное яйцо (мм)", gestationalSac),
                  ("КТР (мм)", crl), ("Срок (нед)", term), ("Желточный мешок (мм)", yolkSac),
                  ("Сердцебиение", heartbeat), ("ЧСС (уд/мин)", hr), ("Хорион", chorion),
                  ("Желтое тело", corpusLuteum), ("Дополнительно", additional),
                  ("Заключение", conclusion), ("Рекомендации", recommendations)]
    elif is_pelvis:
        title = "УЗИ малого таза"
        fields = [("ФИО", f"{clean_value(fio)}\nВозраст: {clean_value(age)}"),
                  ("Последняя менструация", lmp), ("Описание матки", uterus),
                  ("Структура миометрия", myometrium), ("М-эхо", mecho), ("Шейка матки", cervix),
                  ("Правый яичник", right_ovary), ("Левый яичник", left_ovary),
                  ("Дополнительно", additional), ("Свободная жидкость", fluid),
                  ("Заключение", conclusion), ("Рекомендации", recommendations)]
    elif anamnez_morbi.strip() or gyn_anamnez.strip() or birthdate.strip():
        title = "Первичная консультация гинеколога"
        fields = [("ФИО", f"{clean_value(fio)}\nДата рождения: {clean_value(birthdate)}"),
                  ("Жалобы", clean_value(complaints)),
                  ("Анамнез morbi", anamnez_morbi),
                  ("Гинекологический анамнез", gyn_anamnez),
                  ("Менархе", menarche), ("Менструации", menstruation),
                  ("П.М.", last_period), ("Беременности", pregnancies),
                  ("Гинекологические заболевания", gyn_diseases),
                  ("Соматические заболевания", somatic_diseases),
                  ("Объективный статус", objective),
                  ("Молочные железы", breasts), ("Живот", abdomen),
                  ("Диурез", diuresis), ("Стул", stool),
                  ("Наружные половые органы", external_genitals),
                  ("На зеркалах", speculum), ("Выделения", discharge),
                  ("Шейка матки", cervix), ("PV", pv),
                  ("Диагноз", diagnosis), ("Обследование", examination),
                  ("Рекомендации", recommendations)]
    else:
        title = "Консультативное заключение"
        fields = [("ФИО", f"{clean_value(fio)}\nВозраст: {clean_value(age)}"),
                  ("Диагноз", diagnosis), ("Обследование", examination),
                  ("Рекомендации", recommendations)]

    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("DejaVu", "", 12)

    content_lines = []
    for label, value in fields:
        line = f"{label.strip()}: {clean_value(value)}"
        content_lines.append(line)
        pdf.multi_cell(180, 10, line or "-")
        pdf.ln(1)

    pdf.ln(12)
    pdf.set_font("DejaVu", "", 9)

    full_text = "\n".join(content_lines)
    save_to_db(fio, title, full_text)

    protocol_id = get_last_protocol_id()
    filename = f"data/protocols/{protocol_id}.pdf"

    signature_path = "static/signature_transparent.png"
    pdf.set_font("DejaVu", "", 9)
    pdf.cell(0, 6, "врач акушер-гинеколог Куриленко Юлия Сергеевна", ln=True)
    pdf.cell(0, 6, "Телефон: +37455987715", ln=True)
    pdf.cell(0, 6, "Telegram: https://t.me/doc_Kurilenko", ln=True)
    pdf.ln(5)
    if os.path.exists(signature_path):
        pdf.image(signature_path, x=140, w=50)
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
            return HTMLResponse(content=f"Ошибка отправки письма: {str(e)}", status_code=500)

    return FileResponse(filename, media_type="application/pdf", filename="protocol.pdf")

@app.get("/search", response_class=HTMLResponse)
async def search_protocols(request: Request, query: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, fio, date, template FROM protocols WHERE fio LIKE ?", (f"%{query}%",))
    results = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("search.html", {
        "request": request,
        "results": results,
        "query": query
    })

@app.get("/view/{protocol_id}", response_class=FileResponse)
async def view_protocol(protocol_id: int):
    path = f"data/protocols/{protocol_id}.pdf"
    if os.path.exists(path):
        return FileResponse(path, media_type="application/pdf", filename=f"protocol_{protocol_id}.pdf")
    return HTMLResponse("Файл не найден", status_code=404)

@app.get("/download/{protocol_id}", response_class=FileResponse)
async def download_protocol(protocol_id: int):
    path = f"data/protocols/{protocol_id}.pdf"
    if os.path.exists(path):
        return FileResponse(path, media_type="application/pdf", filename=f"protocol_{protocol_id}.pdf")
    return HTMLResponse("Файл не найден", status_code=404)

@app.get("/backup-page", response_class=HTMLResponse)
async def backup_page(request: Request):
    return templates.TemplateResponse("backup.html", {"request": request})

@app.get("/backup", response_class=FileResponse)
async def create_backup():
    zip_path = "/tmp/backup.zip"
    with zipfile.ZipFile(zip_path, "w") as backup_zip:
        if os.path.exists(DB_PATH):
            backup_zip.write(DB_PATH, arcname="database.db")
        for root, dirs, files in os.walk("data/protocols"):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, start="data")
                backup_zip.write(full_path, arcname=rel_path)
    return FileResponse(zip_path, filename="backup.zip", media_type="application/zip")

def get_last_protocol_id():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM protocols")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 1
