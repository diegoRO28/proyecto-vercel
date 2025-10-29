from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html", media_type="text/html; charset=utf-8" )

@app.get("/download-cv")
def downloadcv():
    return FileResponse("static/resume.pdf")