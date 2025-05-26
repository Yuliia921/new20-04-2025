
import os
import sqlite3
import zipfile
from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from email.message import EmailMessage
import smtplib
from fpdf import FPDF
from datetime import datetime

def init_db():
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/protocols", exist_ok=True)
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

    protocol_id = int(datetime.now().timestamp())
    file_path = f"data/protocols/{protocol_id}.pdf"
    pdf.output(file_path)

    save_to_db(fio, template, full_text)

    return FileResponse(file_path, filename="protocol.pdf", media_type="application/pdf")

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
async def serve_backup_page(request: Request):
    return templates.TemplateResponse("backup.html", {"request": request})

@app.get("/backup", response_class=FileResponse)
async def download_backup():
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
