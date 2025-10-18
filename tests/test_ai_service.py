import pytest
import json
from unittest.mock import patch, MagicMock
from app.services.ai_service import AIService
import os

@pytest.fixture
def ai_service():
    """Fixture for AIService."""
    with patch.dict(os.environ, {"AI_PROVIDER": "ollama"}):
        yield AIService()

@pytest.mark.asyncio
@patch("app.services.ollama_service.OllamaService.generate_text")
async def test_ai_service_generate_text(mock_generate_text, ai_service):
    """Test AIService generate_text method."""
    mock_generate_text.return_value = json.dumps({"response": "test"})
    response = await ai_service.generate_text("test prompt")
    assert response == {"response": "test"}

@pytest.mark.asyncio
@patch("app.services.ollama_service.OllamaService.generate_text")
async def test_ai_service_translate_text(mock_generate_text, ai_service):
    """Test AIService translate_text method."""
    mock_generate_text.return_value = json.dumps({"translated_text": "test"})
    response = await ai_service.translate_text("test", "es")
    assert response == "test"

@pytest.mark.asyncio
@patch("app.services.ollama_service.OllamaService.generate_text")
async def test_ai_service_summarize_text(mock_generate_text, ai_service):
    """Test AIService summarize_text method."""
    mock_generate_text.return_value = json.dumps({"summary": "test"})
    response = await ai_service.summarize_text("test")
    assert response == "test"

@pytest.mark.asyncio
@patch("app.services.ollama_service.OllamaService.generate_text")
async def test_ai_service_extract_keywords(mock_generate_text, ai_service):
    """Test AIService extract_keywords method."""
    mock_generate_text.return_value = json.dumps({"keywords": ["test"]})
    response = await ai_service.extract_keywords("test")
    assert response == ["test"]
