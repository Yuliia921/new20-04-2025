
# ... остальной код загружается из твоей версии ...
# заменённая строка:
file_path = f"data/protocols/{protocol_id}.pdf"
# добавленные маршруты в конце:
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
