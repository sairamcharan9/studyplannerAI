import os
import pytest
from fastapi.testclient import TestClient
from main import app # Assuming main.py is where the FastAPI app is instantiated
from app.services.facial_analysis_data_service import FacialAnalysisDataService
import json
import base64
import shutil

client = TestClient(app)

# --- Unit Test for FacialAnalysisDataService ---
@pytest.fixture(scope="function")
def facial_analysis_service_setup():
    test_data_dir = "test_data_facial_analysis"
    # Clean up any previous test data
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    
    service = FacialAnalysisDataService(data_dir=test_data_dir)
    yield service
    # Clean up after test
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)

def test_save_expression_data(facial_analysis_service_setup):
    service = facial_analysis_service_setup
    user_id = "test_user_1"
    study_session_id = "test_session_abc"
    expression = "Happy"
    confidence = 0.95

    service.save_expression_data(user_id, study_session_id, expression, confidence)

    assert os.path.exists(service.log_file)
    with open(service.log_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == 1
        log_entry = json.loads(lines[0])
        assert log_entry["user_id"] == user_id
        assert log_entry["study_session_id"] == study_session_id
        assert log_entry["expression"] == expression
        assert log_entry["confidence"] == confidence
        assert "timestamp" in log_entry

# --- Integration Test for Facial Analysis API Endpoint ---
def test_analyze_expression_success():
    # Create a dummy base64 image (a 1x1 black pixel)
    dummy_image_bytes = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\xda\xed\xc1\x01\x01\x00\x00\x00\xc2\xa0\xf7Om\x00\x00\x00\x00IEND\xaeB`\x82').decode('utf-8')
    # Add the data URI prefix
    image_data_uri = f"data:image/png;base64,{dummy_image_bytes}"

    response = client.post(
        "/api/analyze-expression",
        json={'image': image_data_uri}
    )

    assert response.status_code == 200
    data = response.json()
    assert "expression" in data
    assert "confidence" in data
    assert "message" in data
    assert data["message"] == "Facial analysis performed."
    assert isinstance(data["expression"], str)
    assert isinstance(data["confidence"], float)

def test_analyze_expression_no_image_data():
    response = client.post(
        "/api/analyze-expression",
        json={}
    )
    assert response.status_code == 400
    assert response.json() == {'detail': 'No image data provided'}

def test_analyze_expression_invalid_image_data():
    response = client.post(
        "/api/analyze-expression",
        json={'image': 'data:image/jpeg;base64,invalid-base64'}
    )
    assert response.status_code == 500 # Should be 500 due to decoding error in backend
    # The exact error message might vary depending on base64.b64decode and cv2.imdecode
    assert "Internal server error during analysis" in response.json()['detail']
