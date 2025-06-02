import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from tests.constants import (
    TEST_LOGIN_DATA,
    MOCK_USER_DB_ENTRY,
    API_BASE_URL,
    MOCK_AUTH_RESPONSE,
    TEST_REGISTRATION_DATA,
    HTTP_200_OK,
    HTTP_201_CREATED
)

transport = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_register_user(mocker):
    test_data = TEST_REGISTRATION_DATA

    # Setup mock DB and collection
    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value = MagicMock(inserted_id="123")

    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection

    async def mock_get_db():
        yield mock_db

    # Patch dependencies
    mocker.patch("app.services.user_service.get_db", mock_get_db)
    mock_register_user = mocker.patch(
        "app.services.user_service.register_user",
        new_callable=AsyncMock
    )
    mock_register_user.return_value = {"email": test_data["email"], "id": "123"}

    async with AsyncClient(transport=transport, base_url=API_BASE_URL) as client:
        response = await client.post("/users/register", json=test_data)

    assert response.status_code == HTTP_201_CREATED
    assert response.json()["email"] == test_data["email"]


@pytest.mark.asyncio
async def test_login_user(mocker):
    test_data = TEST_LOGIN_DATA

    # Setup mock DB and collection
    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = MOCK_USER_DB_ENTRY

    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection

    async def mock_get_db():
        yield mock_db

    # Patch dependencies
    mocker.patch("app.services.user_service.get_db", mock_get_db)

    mock_authenticate_user = mocker.patch("app.api.user_routes.authenticate_user", new_callable=AsyncMock)

    mock_authenticate_user.return_value = MOCK_AUTH_RESPONSE

    async with AsyncClient(transport=transport, base_url=API_BASE_URL) as client:
        response = await client.post("/users/login", data=test_data)

    assert response.status_code == HTTP_200_OK
    assert "access_token" in response.json()
