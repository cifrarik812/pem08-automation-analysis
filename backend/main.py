"""Lesson API adapted for local research of automation platforms."""
import base64
import io
import time
from contextlib import asynccontextmanager
from urllib.parse import urlparse
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from PIL import Image, UnidentifiedImageError
from backend.config import settings, ROOT
from backend.models.schemas import (TextAnalysisRequest, TextAnalysisResponse, ImageAnalysisResponse,
    ParseDemoRequest, ParseDemoResponse, ParsedContent, HistoryResponse)
from backend.services.openai_service import openai_service
from backend.services.gigachat_service import AnalysisError
from backend.services.parser_service import parser_service
from backend.services.history_service import history_service

@asynccontextmanager
async def lifespan(app):
    yield
    await parser_service.close()

app=FastAPI(title='Анализатор сервисов автоматизации',version='2.0.0',lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1','localhost','testserver'])

@app.middleware('http')
async def check_origin(request:Request,call_next):
    origin=request.headers.get('origin')
    if request.method not in ('GET','HEAD','OPTIONS') and origin:
        if origin not in (f'http://127.0.0.1:{settings.api_port}',f'http://localhost:{settings.api_port}'):
            return JSONResponse({'detail':'Недопустимый источник запроса'},status_code=403)
    return await call_next(request)

def safe_error(exc):
    if isinstance(exc,AnalysisError):
        return str(exc)
    return 'Не удалось завершить анализ. Проверьте настройки API и локальный журнал.'

@app.get('/')
async def root():
    return FileResponse(ROOT/'frontend'/'index.html')

@app.post('/analyze_text',response_model=TextAnalysisResponse)
async def analyze_text(request:TextAnalysisRequest):
    try:
        started=time.perf_counter()
        analysis=await openai_service.analyze_text(request.text)
        history_service.add_entry(request_type='text',request_summary=request.text[:100],response_summary=analysis.summary,
            result=analysis.model_dump(),source=request.source_url,duration_s=round(time.perf_counter()-started,3))
        return TextAnalysisResponse(success=True,analysis=analysis)
    except Exception as exc:
        return TextAnalysisResponse(success=False,error=safe_error(exc))

@app.post('/analyze_image',response_model=ImageAnalysisResponse)
async def analyze_image(file:UploadFile=File(...)):
    content=await file.read(10*1024*1024+1)
    if len(content)>10*1024*1024:
        raise HTTPException(413,'Изображение должно быть не больше 10 МБ')
    try:
        with Image.open(io.BytesIO(content)) as image:
            mime=Image.MIME.get(image.format)
            if mime not in ('image/png','image/jpeg') or mime!=file.content_type:
                raise ValueError('MIME mismatch')
            if max(image.size)>8192 or image.width*image.height>24000000:
                raise ValueError('Image dimensions too large')
            image.verify()
    except (ValueError,UnidentifiedImageError,OSError,Image.DecompressionBombError):
        raise HTTPException(400,'Нужен настоящий PNG или JPG с верным типом, до 8192 пикселей и 24 Мп')
    try:
        started=time.perf_counter()
        analysis=await openai_service.analyze_image(base64.b64encode(content).decode(),file.content_type)
        history_service.add_entry(request_type='image',request_summary=f'Изображение: {file.filename}',response_summary=analysis.description,
            result=analysis.model_dump(),source=file.filename,duration_s=round(time.perf_counter()-started,3))
        return ImageAnalysisResponse(success=True,analysis=analysis)
    except Exception as exc:
        return ImageAnalysisResponse(success=False,error=safe_error(exc))

@app.post('/parse_demo',response_model=ParseDemoResponse)
async def parse_demo(request:ParseDemoRequest):
    try:
        started=time.perf_counter()
        title,h1,paragraph,screenshot,error=await parser_service.parse_url(request.url)
        if error:
            return ParseDemoResponse(success=False,error=error)
        if not screenshot:
            return ParseDemoResponse(success=False,error='Парсер не получил снимок страницы')
        analysis=await openai_service.analyze_website_screenshot(base64.b64encode(screenshot).decode(),request.url,title,h1,paragraph)
        data=ParsedContent(url=request.url,title=title,h1=h1,first_paragraph=paragraph,analysis=analysis)
        history_service.add_entry(request_type='parse',request_summary=request.url,response_summary=analysis.summary,
            result=analysis.model_dump(),source=request.url,duration_s=round(time.perf_counter()-started,3))
        return ParseDemoResponse(success=True,data=data)
    except Exception as exc:
        return ParseDemoResponse(success=False,error=safe_error(exc))

@app.get('/history',response_model=HistoryResponse)
async def get_history():
    items=history_service.get_history()
    return HistoryResponse(items=items,total=len(items))

@app.delete('/history')
async def clear_history():
    history_service.clear_history()
    return {'success':True,'message':'История очищена'}

@app.get('/health')
async def health_check():
    return {'status':'healthy','service':'PEM08 Automation Research','version':'2.0.0','provider':'GigaChat'}

app.mount('/static',StaticFiles(directory=ROOT/'frontend'),name='static')
