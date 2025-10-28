from fastapi import FastAPI, Request, UploadFile, File, Response
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.processors import export_voetbal_from_xlsx_bytes, export_overig_from_xlsx_bytes
import io
import pathlib

app = FastAPI(title="DL regiosport codefixer", version="1.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def _make_txt_stream(data: str, filename: str) -> StreamingResponse:
    buf = io.BytesIO(data.encode("utf-8"))
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(buf, media_type="text/plain; charset=utf-8", headers=headers)

from fastapi import HTTPException
import traceback, logging
logger = logging.getLogger("uvicorn.error")

@app.post("/api/voetbal")
async def api_voetbal(file: UploadFile = File(...)):
    try:
        content = await file.read()
        txt = export_voetbal_from_xlsx_bytes(content)
        return _make_txt_stream(txt, "opmaakscript_voetbal.txt")
    except Exception as e:
        logger.error("Voetbal export crash:\n%s", traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Voetbal: {e}")

@app.post("/api/overig")
async def api_overig(file: UploadFile = File(...)):
    try:
        content = await file.read()
        txt = export_overig_from_xlsx_bytes(content)
        return _make_txt_stream(txt, "opmaakscript_overig.txt")
    except Exception as e:
        logger.error("Overig export crash:\n%s", traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Overig: {e}")

@app.get("/download/template/{kind}")
def download_template(kind: str):
    fn_map = {
        "voetbal": "samples/Invulbestand_amateursport_voetbal.xlsx",
        "overig": "samples/Invulbestand_amateursport_overig.xlsx",
    }
    path = fn_map.get(kind)
    if not path:
        return PlainTextResponse("Onbekend template.", status_code=404)
    return FileResponse(path, filename=pathlib.Path(path).name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
