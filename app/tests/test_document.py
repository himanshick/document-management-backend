# app/tests/test_document.py

import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_upload_document_success(monkeypatch):
    async def mock_upload(file, user_id):
        return {"id": "abc123", "filename": "test.txt", "content_type": "text/plain", "uploaded_by": user_id}

    monkeypatch.setattr("app.services.document_service.upload_document", mock_upload)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/documents/upload",
            files={"file": ("test.txt", b"sample content", "text/plain")},
            headers={"Authorization": "Bearer dummy_token"}
        )
    assert response.status_code == 200
    assert response.json()["filename"] == "test.txt"

@pytest.mark.asyncio
async def test_get_document_success(monkeypatch):
    async def mock_get_document(doc_id, user_id):
        return {"id": doc_id, "filename": "test.txt", "uploaded_by": user_id}

    monkeypatch.setattr("app.services.document_service.get_document_by_id", mock_get_document)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/documents/abc123", headers={"Authorization": "Bearer dummy_token"})
    assert response.status_code == 200
    assert response.json()["id"] == "abc123"

@pytest.mark.asyncio
async def test_list_documents(monkeypatch):
    async def mock_list(user_id):
        return [{"id": "abc123", "filename": "test.txt", "uploaded_by": user_id}]

    monkeypatch.setattr("app.services.document_service.list_user_documents", mock_list)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/documents", headers={"Authorization": "Bearer dummy_token"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["filename"] == "test.txt"
