"""Analysis contract and upload boundary tests; no external API calls."""
import asyncio
import base64
import io
import json
import os

import pytest
from PIL import Image
from pydantic import ValidationError

# Importing the upstream service required an API key even for JSON parsing.
os.environ.setdefault("PROXY_API_KEY", "test-key-never-used")

from backend.config import Settings
from backend.models.schemas import CompetitorAnalysis, ImageAnalysis
from backend.services.openai_service import OpenAIService


def competitor_payload(**updates):
    value = {
        "strengths": ["В тексте заявлены интеграции"],
        "weaknesses": [],
        "unique_offers": [],
        "recommendations": ["Проверить интеграции на своей задаче"],
        "summary": "Наблюдения по предоставленному тексту",
        "automation_fit": "Подходит для проверки автоматизации",
        "design_score": None,
        "animation_potential": "Гипотеза: показать поток данных",
        "limitations": ["Тарифы и надёжность не проверялись"],
    }
    return value | updates


def image_payload(**updates):
    value = {
        "description": "Снимок страницы сервиса",
        "marketing_insights": ["Виден заголовок"],
        "visual_style_score": 7,
        "visual_style_analysis": "Читаемый заголовок",
        "recommendations": ["Проверить контраст"],
        "automation_fit": "Сценарий требует проверки",
        "design_score": 7,
        "animation_potential": "Гипотеза: анимировать схему",
        "limitations": ["Статичный снимок не подтверждает анимацию"],
    }
    return value | updates


@pytest.mark.parametrize("content", ["not json", "[]", "null", '{"summary":', 'prefix {"summary":"x"} suffix'])
def test_invalid_json_is_an_error_not_an_empty_success(content):
    with pytest.raises(ValueError):
        OpenAIService()._parse_json_response(content)


@pytest.mark.parametrize("model", [CompetitorAnalysis, ImageAnalysis])
def test_missing_required_fields_cannot_become_success(model):
    with pytest.raises(ValidationError):
        model.model_validate({})


@pytest.mark.parametrize("score", [-1, 11, "7", True])
def test_design_score_is_strict_and_within_bounds(score):
    with pytest.raises(ValidationError):
        CompetitorAnalysis.model_validate(competitor_payload(design_score=score))


def test_valid_text_contract_keeps_null_design_score():
    analysis = CompetitorAnalysis.model_validate(competitor_payload())
    assert analysis.model_dump()["design_score"] is None
    assert analysis.automation_fit == "Подходит для проверки автоматизации"


@pytest.mark.parametrize("field", ["summary", "automation_fit", "animation_potential"])
def test_blank_analysis_claims_are_rejected(field):
    with pytest.raises(ValidationError):
        CompetitorAnalysis.model_validate(competitor_payload(**{field: "   "}))


@pytest.mark.parametrize("score", [-1, 11, "7", True])
def test_visual_style_score_rejects_invalid_or_coerced_values(score):
    with pytest.raises(ValidationError):
        ImageAnalysis.model_validate(image_payload(visual_style_score=score))


def test_server_config_rejects_public_bind_address():
    with pytest.raises(ValidationError):
        Settings(api_host="0.0.0.0")


@pytest.fixture
def api_client(monkeypatch):
    from fastapi.testclient import TestClient
    from backend import main

    async def analyzed(*args, **kwargs):
        return ImageAnalysis.model_validate(image_payload())

    monkeypatch.setattr(main.openai_service, "analyze_image", analyzed)
    monkeypatch.setattr(main.history_service, "add_entry", lambda **kwargs: None)
    return TestClient(main.app)


def png_bytes(size=(8, 8)):
    stream = io.BytesIO()
    Image.new("RGB", size).save(stream, format="PNG")
    return stream.getvalue()


@pytest.mark.parametrize("content,mime", [(b"not an image", "image/jpeg"), (png_bytes(), "image/jpeg")])
def test_spoofed_image_is_rejected_before_analysis(api_client, content, mime):
    response = api_client.post("/analyze_image", files={"file": ("image.jpg", content, mime)})
    assert response.status_code == 400


def test_oversized_upload_is_rejected(api_client):
    response = api_client.post("/analyze_image", files={"file": ("large.png", b"x" * (10 * 1024 * 1024 + 1), "image/png")})
    assert response.status_code == 413


def test_oversized_dimensions_are_rejected(api_client):
    response = api_client.post("/analyze_image", files={"file": ("wide.png", png_bytes((8193, 1)), "image/png")})
    assert response.status_code == 400


def test_real_image_with_matching_mime_can_be_analyzed(api_client):
    response = api_client.post("/analyze_image", files={"file": ("image.png", png_bytes(), "image/png")})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["analysis"]["design_score"] == 7


def test_unexpected_provider_error_is_not_exposed(api_client, monkeypatch):
    from backend import main

    async def failed(*args, **kwargs):
        raise RuntimeError("Authorization: Bearer private-secret-token")

    monkeypatch.setattr(main.openai_service, "analyze_text", failed)
    response = api_client.post("/analyze_text", json={"text": "Automation public source"})
    assert response.json()["success"] is False
    assert "private-secret-token" not in response.text
