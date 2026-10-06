"""Compatibility import for the lesson's original interface. Provider is GigaChat."""
from backend.services.gigachat_service import GigaChatService
OpenAIService = GigaChatService
openai_service = GigaChatService()
