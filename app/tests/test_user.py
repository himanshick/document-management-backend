# app/tests/test_user.py

import pytest
from httpx import AsyncClient
from app.main import app
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_register_user(monkeypatch):
    async def mock_register_user(user):
        return {"id": "fakeid123", "email": user.email}
    
    monkeypatch.setattr("app.services.user_service.register_user", mock_register_user)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/users/register", json={
            "email": "test@example.com",
            "password": "strongpassword123",
            "full_name": "Test User"
        })
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "fakeid123"
    assert data["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_login_user(monkeypatch):
    async def mock_authenticate_user(email, password):
        return {"access_token": "fakejwttoken", "token_type": "bearer"}

    monkeypatch.setattr("app.services.user_service.authenticate_user", mock_authenticate_user)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/users/login", data={
            "username": "test@example.com",
            "password": "strongpassword123"
        })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
