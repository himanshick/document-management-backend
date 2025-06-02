import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import get_current_user
from app.models.document import DocumentInDB

from tests.constants import (
    API_BASE_URL,
    TEST_USER_ID,
    TEST_DOCUMENT_ID,
    TEST_DOCUMENT,
    UPDATED_DOCUMENT_DATA,
)


# Dependency override to simulate authenticated user
def override_get_current_user():
    class FakeUser:
        def __init__(self):
            self._id = TEST_USER_ID
            self.role = "viewer"
    return FakeUser()

app.dependency_overrides[get_current_user] = override_get_current_user

transport = ASGITransport(app=app)

@pytest.fixture
def test_document():
    return TEST_DOCUMENT.copy()

@pytest.mark.asyncio
async def test_create_document(test_document):
    doc_create = {
        "title": test_document["title"],
        "content": test_document["content"],
    }

    with patch("app.api.document_routes.create_document", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = DocumentInDB(**test_document)

        async with AsyncClient(transport=transport, base_url=API_BASE_URL) as ac:
            response = await ac.post("/documents/", json=doc_create)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == test_document["title"]

@pytest.mark.asyncio
async def test_get_document_by_id(test_document):
    with patch("app.api.document_routes.get_document", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = DocumentInDB(**test_document)

        async with AsyncClient(transport=transport, base_url=API_BASE_URL) as ac:
            response = await ac.get(f"/documents/{test_document['_id']}")

        assert response.status_code == 200
        assert response.json()["_id"] == test_document["_id"]

@pytest.mark.asyncio
async def test_get_document_not_found():
    with patch("app.api.document_routes.get_document", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None

        async with AsyncClient(transport=transport, base_url=API_BASE_URL) as ac:
            response = await ac.get("/documents/nonexistent")

        assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_all_documents(test_document):
    with patch("app.api.document_routes.get_all_documents", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [DocumentInDB(**test_document)]

        async with AsyncClient(transport=transport, base_url=API_BASE_URL) as ac:
            response = await ac.get("/documents/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert response.json()[0]["_id"] == test_document["_id"]

@pytest.mark.asyncio
async def test_update_document(test_document):
    updated_doc = {
        **test_document,
        **UPDATED_DOCUMENT_DATA,
    }

    with patch("app.api.document_routes.update_document", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = DocumentInDB(**updated_doc)

        async with AsyncClient(transport=transport, base_url=API_BASE_URL) as ac:
            response = await ac.put(f"/documents/{test_document['_id']}", json=UPDATED_DOCUMENT_DATA)

        assert response.status_code == 200
        assert response.json()["title"] == UPDATED_DOCUMENT_DATA["title"]

@pytest.mark.asyncio
async def test_delete_document(test_document):
    with patch("app.api.document_routes.delete_document", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True

        async with AsyncClient(transport=transport, base_url=API_BASE_URL) as ac:
            response = await ac.delete(f"/documents/{test_document['_id']}")

        assert response.status_code == 200
        assert response.json()["message"] == "Document deleted successfully"
