# app/tests/test_ingestion.py

import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_trigger_ingestion(monkeypatch):
    async def mock_trigger(tenant_id):
        return {"message": f"Ingestion triggered for tenant {tenant_id}"}

    monkeypatch.setattr("app.services.ingestion_service.trigger_ingestion_for_tenant", mock_trigger)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/ingestion/trigger/tenant123")
    assert response.status_code == 200
    assert response.json()["message"] == "Ingestion triggered for tenant tenant123"

@pytest.mark.asyncio
async def test_get_ingestion_status(monkeypatch):
    async def mock_status(tenant_id):
        return {"tenant_id": tenant_id, "status": "completed"}

    monkeypatch.setattr("app.services.ingestion_service.get_ingestion_status", mock_status)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/ingestion/status/tenant123")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
