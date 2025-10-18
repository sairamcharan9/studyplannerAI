import pytest
import json
from unittest.mock import patch, MagicMock
from app.services.study_plan_service import StudyPlanService
from app.services.ai_service import AIService

@pytest.fixture
def study_plan_service():
    """Fixture for StudyPlanService."""
    return StudyPlanService()

@pytest.fixture
def mock_ai_service():
    """Fixture for a mocked AIService."""
    mock = MagicMock(spec=AIService)
    mock.provider_name = "ollama"
    return mock

@pytest.mark.asyncio
@patch("app.services.research_service.ResearchService.research_topic")
async def test_generate_plan(mock_research_topic, study_plan_service, mock_ai_service):
    """Test StudyPlanService generate_plan method."""
    mock_research_topic.return_value = {"content": "test"}
    mock_ai_service.generate_text.return_value = {
        "summary": "test summary",
        "prerequisites": ["test prereq"],
        "quiz": [{"question": "test question"}],
    }

    response = await study_plan_service.generate_plan(
        "test topic",
        mock_research_topic.return_value,
        mock_ai_service,
    )

    assert response["summary"] == "[Generated using: OLLAMA] test summary"
    assert response["prerequisites"] == ["test prereq"]
    assert response["quiz"] == [{"question": "test question"}]
