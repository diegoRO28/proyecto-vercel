from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import os
import smtplib
from email.message import EmailMessage

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html", media_type="text/html; charset=utf-8" )


@app.get("/download-cv")
def downloadcv():
    return FileResponse("static/resume.pdf")


# Contact POST endpoint: reads SMTP credentials from environment variables:
# SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
class ContactIn(BaseModel):
    name: str
    email: EmailStr
    message: str


@app.post('/contact')
def send_contact(payload: ContactIn):
    # Load SMTP settings from env
    host = os.getenv('SMTP_HOST')
    port = os.getenv('SMTP_PORT')
    user = os.getenv('SMTP_USER')
    password = os.getenv('SMTP_PASS')

    if not (host and port and user and password):
        # Server not configured for SMTP
        raise HTTPException(status_code=501, detail='SMTP no configurado en el servidor. Usa mailto o configura las variables SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASS')

    try:
        port_i = int(port)
    except Exception:
        raise HTTPException(status_code=500, detail='Puerto SMTP inválido')

    # Build email
    msg = EmailMessage()
    msg['Subject'] = f'Contacto desde portafolio — {payload.name}'
    msg['From'] = user
    msg['To'] = user
    msg['Reply-To'] = payload.email
    body = f"Nombre: {payload.name}\nEmail: {payload.email}\n\nMensaje:\n{payload.message}"
    msg.set_content(body)

    # Send using SSL if common port 465, otherwise try STARTTLS
    try:
        if port_i == 465:
            with smtplib.SMTP_SSL(host, port_i) as server:
                server.login(user, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port_i, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.login(user, password)
                server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f'Error enviando email: {e}')

    return JSONResponse({'status': 'ok', 'message': 'Correo enviado (o en cola)'} )