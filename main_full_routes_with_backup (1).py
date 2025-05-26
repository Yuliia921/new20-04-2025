
import os
import sqlite3
import zipfile
from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from email.message import EmailMessage
import smtplib
from uuid import uuid4
from fpdf import FPDF
from datetime import datetime

# Настройка базы данных
os.makedirs("data/protocols", exist_ok=True)
DB_PATH = "data/database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
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

def save_to_db(fio, template, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO protocols (fio, date, template, content) VALUES (?, ?, ?, ?)",
                   (fio.strip(), date, template, content))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def clean_value(text):
    if not text or text.strip() == "":
        return "-"
    return text.strip().replace("🌸", "").replace("💬", "").replace("📤", "")

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
    filepath = f"data/protocols/{protocol_id}.pdf"
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="application/pdf", filename=f"protocol_{protocol_id}.pdf")
    return HTMLResponse(content="Файл не найден", status_code=404)

@app.get("/backup", response_class=FileResponse)
async def create_backup():
    zip_filename = "backup.zip"
    with zipfile.ZipFile(zip_filename, "w") as backup_zip:
        if os.path.exists(DB_PATH):
            backup_zip.write(DB_PATH, arcname="database.db")
        for root, dirs, files in os.walk("data/protocols"):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, start="data")
                backup_zip.write(filepath, arcname=os.path.join("protocols", arcname))
    return FileResponse(zip_filename, media_type="application/zip", filename=zip_filename)

@app.get("/backup-page", response_class=HTMLResponse)
async def backup_page(request: Request):
    return templates.TemplateResponse("backup.html", {"request": request})

@app.post("/generate_pdf")
async def generate_pdf(
    request: Request,
    fio: str = Form(""),
    email: str = Form(""),
    content: str = Form(""),
    template: str = Form("Консультативное заключение")
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)

    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, template, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("DejaVu", "", 12)

    lines = content.strip().split("\n")
    full_text = ""
    for line in lines:
        pdf.multi_cell(180, 10, clean_value(line))
        pdf.ln(1)
        full_text += clean_value(line) + "\n"

    pdf.ln(12)
    pdf.set_font("DejaVu", "", 9)
    pdf.cell(0, 6, "врач акушер-гинеколог Куриленко Юлия Сергеевна", ln=True)
    pdf.cell(0, 6, "Телефон: +37455987715", ln=True)
    pdf.cell(0, 6, "Telegram: https://t.me/doc_Kurilenko", ln=True)
    pdf.ln(5)

    protocol_id = save_to_db(fio, template, full_text)
    filepath = f"data/protocols/{protocol_id}.pdf"
    pdf.output(filepath)

    if email.strip():
        try:
            smtp_user = os.getenv("SMTP_USER")
            smtp_pass = os.getenv("SMTP_PASS")

            msg = EmailMessage()
            msg["Subject"] = "Ваш протокол из Док Куриленко"
            msg["From"] = smtp_user
            msg["To"] = email.strip()
            msg.set_content("Здравствуйте! Во вложении — ваш протокол в формате PDF.\n\nС уважением,\nКуриленко Ю.С.")

            with open(filepath, "rb") as f:
                msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="protocol.pdf")

            with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as smtp:
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg)

        except Exception as e:
            return HTMLResponse(content=f"Ошибка отправки письма: {str(e)}", status_code=500)

    return FileResponse(filepath, media_type="application/pdf", filename="protocol.pdf")
