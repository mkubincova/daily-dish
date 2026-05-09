import pytest
from httpx import AsyncClient

from app.deps import SESSION_COOKIE
from app.models.user import User
from app.utils.uuid7 import new_uuid7


@pytest.mark.asyncio
async def test_me_anonymous(client: AsyncClient):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(auth_client: AsyncClient, user: User):
    resp = await auth_client.get("/api/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == user.email
    assert data["name"] == user.name
    assert "provider" in data


@pytest.mark.asyncio
async def test_logout_clears_cookie(auth_client: AsyncClient):
    resp = await auth_client.post("/api/auth/logout")
    assert resp.status_code == 200
    # Cookie should be cleared
    assert SESSION_COOKIE not in resp.cookies or resp.cookies[SESSION_COOKIE] == ""


@pytest.mark.asyncio
async def test_tampered_cookie_rejected(client: AsyncClient, session, user: User):
    from app.database import get_session
    from app.main import app

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session

    from httpx import ASGITransport
    from httpx import AsyncClient as AC

    from app.main import app as the_app

    async with AC(
        transport=ASGITransport(app=the_app),
        base_url="http://test",
        cookies={SESSION_COOKIE: "tampered.invalid.cookie"},
    ) as ac:
        resp = await ac.get("/api/auth/me")
        assert resp.status_code == 401

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_oauth_login_redirect_uri_uses_forwarded_host(
    monkeypatch: pytest.MonkeyPatch, client: AsyncClient
):
    """The OAuth redirect_uri must be built off X-Forwarded-Host so the
    URL registered with the upstream provider (Vercel origin) matches
    what gets sent in the authorize request."""
    monkeypatch.setenv("GITHUB_CLIENT_ID", "test-client")
    monkeypatch.setenv("GITHUB_CLIENT_SECRET", "test-secret")

    from urllib.parse import parse_qs, urlparse

    from authlib.integrations.starlette_client import OAuth

    from app.routers import auth as auth_module

    fresh_oauth = OAuth()
    fresh_oauth.register(
        name="github",
        client_id="test-client",
        client_secret="test-secret",
        authorize_url="https://github.com/login/oauth/authorize",
        access_token_url="https://github.com/login/oauth/access_token",
        client_kwargs={"scope": "user:email"},
    )
    monkeypatch.setattr(auth_module, "oauth", fresh_oauth)

    resp = await client.get(
        "/api/auth/github/login",
        headers={
            "x-original-host": "daily-dish-dsfs.vercel.app",
            "x-original-proto": "https",
        },
        follow_redirects=False,
    )
    assert resp.status_code in (302, 307)
    location = resp.headers["location"]
    parsed = urlparse(location)
    redirect_uri = parse_qs(parsed.query)["redirect_uri"][0]
    assert "daily-dish-dsfs.vercel.app" in redirect_uri
    assert redirect_uri.endswith("/api/auth/github/callback")


@pytest.mark.asyncio
async def test_upsert_creates_new_user(session):
    """Verify user upsert logic directly — new user gets created."""
    from sqlmodel import select

    from app.models.user import User

    # No user exists yet
    result = await session.exec(
        select(User).where(User.provider == "github", User.provider_id == "newuser123")
    )
    assert result.first() is None

    # Create one
    u = User(
        id=new_uuid7(),
        email="new@example.com",
        name="New User",
        provider="github",
        provider_id="newuser123",
    )
    session.add(u)
    await session.commit()

    result = await session.exec(
        select(User).where(User.provider == "github", User.provider_id == "newuser123")
    )
    assert result.first() is not None


@pytest.mark.asyncio
async def test_same_email_different_provider_creates_separate_accounts(session):
    """Accounts are keyed by (provider, provider_id), not email."""
    u1 = User(
        id=new_uuid7(),
        email="shared@example.com",
        name="User1",
        provider="github",
        provider_id="g1",
    )
    u2 = User(
        id=new_uuid7(),
        email="shared@example.com",
        name="User2",
        provider="google",
        provider_id="g2",
    )
    session.add(u1)
    session.add(u2)
    await session.commit()

    from sqlmodel import select

    result = await session.exec(select(User).where(User.email == "shared@example.com"))
    users = result.all()
    assert len(users) == 2


@pytest.mark.asyncio
async def test_test_login_creates_user_and_sets_cookie(client: AsyncClient):
    resp = await client.post(
        "/api/auth/_test/login",
        json={"email": "e2e@example.com", "name": "E2E User"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "e2e@example.com"
    assert data["provider"] == "test"
    assert SESSION_COOKIE in resp.cookies

    # Cookie is real — /auth/me should accept it.
    me = await client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "e2e@example.com"


@pytest.mark.asyncio
async def test_test_login_is_idempotent(client: AsyncClient):
    first = await client.post("/api/auth/_test/login", json={"email": "same@example.com"})
    second = await client.post("/api/auth/_test/login", json={"email": "same@example.com"})
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]


@pytest.mark.asyncio
async def test_test_login_disabled_in_production(
    monkeypatch: pytest.MonkeyPatch, client: AsyncClient
):
    from app.routers import auth as auth_module

    monkeypatch.setattr(auth_module.settings, "environment", "production")

    resp = await client.post("/api/auth/_test/login", json={"email": "blocked@example.com"})
    assert resp.status_code == 404
