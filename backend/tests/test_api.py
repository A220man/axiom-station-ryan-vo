import pytest
from fastapi.testclient import TestClient
from app.main import create_app

client = TestClient(create_app())


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_document():
    content = """# Test Lesson

## Hook
Model has 11B parameters.

## Body
Actually uses 6.7B parameters.
"""
    response = client.post(
        "/api/v1/documents/analyze",
        json={"content": content, "phase": "phase-12", "lesson_id": "test-01"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "document" in data
    assert "contradictions" in data
    assert "summary" in data
    assert data["document"]["lesson_id"] == "test-01"
    assert len(data["contradictions"]) >= 1


def test_analyze_file():
    content = """# Test

## Hook
11B LLM

## Body
6.7B model
"""
    files = {"file": ("test.md", content, "text/markdown")}
    data = {"phase": "phase-12", "lesson_id": "test-file"}
    response = client.post("/api/v1/documents/analyze/file", files=files, data=data)
    assert response.status_code == 200
    result = response.json()
    assert result["document"]["lesson_id"] == "test-file"