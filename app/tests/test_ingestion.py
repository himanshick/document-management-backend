import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient
from app.main import app  # Adjust import if needed
from httpx import ASGITransport
from tests.constants import (
    API_BASE_URL,
    TEST_TOKEN,
    AUTH_HEADER_TEMPLATE,
    INGESTION_TRIGGER_ENDPOINT,
    REQUEST_DATA_INGESTION_TRIGGER,
    REQUEST_DATA_INGESTION_TRIGGER_FAILURE,
    MOCK_DECODED_TOKEN_PAYLOAD,
    HTTP_202_ACCEPTED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

transport = ASGITransport(app=app)

@pytest.fixture
def test_token():
    return TEST_TOKEN

@pytest.mark.asyncio
async def test_trigger_ingestion_success(mocker, test_token):
    mock_insert_one = AsyncMock()

    mock_collection = MagicMock()
    mock_collection.insert_one = mock_insert_one

    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection

    async def mock_get_db():
        yield mock_db
    mocker.patch("app.services.ingestion_service.get_db", new=mock_get_db)

    mock_bg_task = AsyncMock()
    mocker.patch("app.services.ingestion_service.run_ingestion_worker", new=mock_bg_task)

    mocker.patch("app.api.ingestion_routes.decode_access_token", return_value=MOCK_DECODED_TOKEN_PAYLOAD)

    headers = {"Authorization": AUTH_HEADER_TEMPLATE.format(test_token)}

    async with AsyncClient(transport=transport, base_url=API_BASE_URL) as client:
        response = await client.post(
            INGESTION_TRIGGER_ENDPOINT,
            headers=headers,
            json=REQUEST_DATA_INGESTION_TRIGGER
        )

    assert response.status_code == HTTP_202_ACCEPTED


@pytest.mark.asyncio
async def test_trigger_ingestion_db_failure(mocker, test_token):
    mock_collection = MagicMock()
    async def insert_one_fail(*args, **kwargs):
        raise Exception("DB failure")
    mock_collection.insert_one = AsyncMock(side_effect=insert_one_fail)

    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection

    async def mock_get_db():
        yield mock_db
    mocker.patch("app.services.ingestion_service.get_db", new=mock_get_db)

    mocker.patch("app.api.ingestion_routes.decode_access_token", return_value=MOCK_DECODED_TOKEN_PAYLOAD)

    headers = {"Authorization": AUTH_HEADER_TEMPLATE.format(test_token)}

    async with AsyncClient(transport=transport, base_url=API_BASE_URL) as client:
        response = await client.post(
            INGESTION_TRIGGER_ENDPOINT,
            headers=headers,
            json=REQUEST_DATA_INGESTION_TRIGGER_FAILURE
        )

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
