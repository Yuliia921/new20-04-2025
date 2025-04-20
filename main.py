
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import smtplib
from email.message import EmailMessage
import os

app = FastAPI()

@app.post("/send_email")
async def send_email(email: str = Form(...), file: UploadFile = File(...)):
    try:
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")

        msg = EmailMessage()
        msg["Subject"] = "Ваш протокол из Док Куриленко"
        msg["From"] = smtp_user
        msg["To"] = email
        msg.set_content("Здравствуйте! Во вложении — ваш протокол в формате PDF.\n\nС уважением,\nврач акушер-гинеколог Куриленко Юлия Сергеевна")

        content = await file.read()
        msg.add_attachment(content, maintype="application", subtype="pdf", filename=file.filename)

        with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)

        return JSONResponse(content={"message": "Письмо успешно отправлено"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/pregnancy.html")

@app.get("/consultation")
async def consultation():
    return FileResponse("static/consultation.html")
