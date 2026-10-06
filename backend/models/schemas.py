"""
Pydantic схемы для API
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, StringConstraints
from typing import Annotated

Nonblank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Score = Annotated[int, Field(strict=True, ge=0, le=10)]

class AnalysisBase(BaseModel):
    model_config = ConfigDict(extra='forbid')
    automation_fit: Nonblank
    design_score: Optional[Score]
    animation_potential: Nonblank
    limitations: List[Nonblank] = Field(min_length=1)


# === Запросы ===

class TextAnalysisRequest(BaseModel):
    """Запрос на анализ текста"""
    text: str = Field(..., min_length=10, max_length=16000, description="Текст для анализа")
    source_url: Optional[str] = None


class ParseDemoRequest(BaseModel):
    """Запрос на парсинг URL"""
    url: str = Field(..., description="URL для парсинга")


# === Ответы ===

class CompetitorAnalysis(AnalysisBase):
    """Структурированный анализ конкурента"""
    strengths: List[Nonblank]
    weaknesses: List[Nonblank]
    unique_offers: List[Nonblank]
    recommendations: List[Nonblank]
    summary: Nonblank


class ImageAnalysis(AnalysisBase):
    """Анализ изображения"""
    description: Nonblank
    marketing_insights: List[Nonblank]
    visual_style_score: Score
    visual_style_analysis: Nonblank
    recommendations: List[Nonblank]


class ParsedContent(BaseModel):
    """Результат парсинга страницы"""
    url: str
    title: Optional[str] = None
    h1: Optional[str] = None
    first_paragraph: Optional[str] = None
    analysis: Optional[CompetitorAnalysis] = None
    error: Optional[str] = None


class TextAnalysisResponse(BaseModel):
    """Ответ на анализ текста"""
    success: bool
    analysis: Optional[CompetitorAnalysis] = None
    error: Optional[str] = None


class ImageAnalysisResponse(BaseModel):
    """Ответ на анализ изображения"""
    success: bool
    analysis: Optional[ImageAnalysis] = None
    error: Optional[str] = None


class ParseDemoResponse(BaseModel):
    """Ответ на парсинг"""
    success: bool
    data: Optional[ParsedContent] = None
    error: Optional[str] = None


# === История ===

class HistoryItem(BaseModel):
    """Элемент истории"""
    id: str
    timestamp: datetime
    request_type: str  # "text", "image", "parse"
    request_summary: str
    response_summary: str
    result: Optional[dict] = None
    source: Optional[str] = None
    duration_s: Optional[float] = None


class HistoryResponse(BaseModel):
    """Ответ со списком истории"""
    items: List[HistoryItem]
    total: int

