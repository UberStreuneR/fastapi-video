from fastapi import FastAPI, Request, Response, Header
from fastapi.responses import StreamingResponse
from pathlib import Path
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from io import BytesIO


# app = FastAPI(docs_url=None, redoc_url=None)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/docs", include_in_schema=False)
# async def custom_swagger_ui_html():
#     return get_swagger_ui_html(
#         openapi_url=app.openapi_url,
#         title=app.title + " - Swagger UI",
#         oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
#         swagger_js_url="/static/swagger-ui-bundle.js",
#         swagger_css_url="/static/swagger-ui.css",
#     )

# @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
# async def swagger_ui_redirect():
#     return get_swagger_ui_oauth2_redirect_html()

templates = Jinja2Templates(directory="templates")
CHUNK_SIZE = 1024*1024
video_path = Path("static/video.mp4")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/video")
async def video_endpoint(range: str = Header(None)):
    start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + CHUNK_SIZE
    with open(video_path, 'rb') as video:
        video.seek(start)
        data = video.read(end-start)
        filesize = str(video_path.stat().st_size)
        headers = {
            'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
            'Accept-Ranges': 'bytes'

        }
        return StreamingResponse(BytesIO(data), status_code=206, headers=headers, media_type="multipart/x-mixed-replace;boundary=frame")
