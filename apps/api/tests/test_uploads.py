import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_sign_upload_requires_auth(client: AsyncClient):
    resp = await client.post("/api/uploads/sign")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_sign_upload_returns_params(auth_client: AsyncClient, user: User, monkeypatch):
    import app.config as cfg_module

    monkeypatch.setattr(cfg_module.settings, "cloudinary_cloud_name", "testcloud")
    monkeypatch.setattr(cfg_module.settings, "cloudinary_api_key", "testkey")
    monkeypatch.setattr(cfg_module.settings, "cloudinary_api_secret", "testsecret")

    resp = await auth_client.post("/api/uploads/sign")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cloud_name"] == "testcloud"
    assert data["api_key"] == "testkey"
    assert "timestamp" in data
    assert "signature" in data
    # Verify signature is a valid sha1 hex string
    assert len(data["signature"]) == 40


@pytest.mark.asyncio
async def test_sign_upload_signature_valid(auth_client: AsyncClient, monkeypatch):
    import hashlib

    import app.config as cfg_module

    monkeypatch.setattr(cfg_module.settings, "cloudinary_cloud_name", "testcloud")
    monkeypatch.setattr(cfg_module.settings, "cloudinary_api_key", "testkey")
    monkeypatch.setattr(cfg_module.settings, "cloudinary_api_secret", "mysecret")

    resp = await auth_client.post("/api/uploads/sign")
    data = resp.json()

    folder = data["folder"]
    timestamp = data["timestamp"]
    expected = hashlib.sha1(f"folder={folder}&timestamp={timestamp}mysecret".encode()).hexdigest()
    assert data["signature"] == expected
