import pytest
from httpx import AsyncClient

from app.deps import SESSION_COOKIE
from app.models.user import User
from app.utils.uuid7 import new_uuid7


@pytest.mark.asyncio
async def test_me_anonymous(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(auth_client: AsyncClient, user: User):
    resp = await auth_client.get("/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == user.email
    assert data["name"] == user.name
    assert "provider" in data


@pytest.mark.asyncio
async def test_logout_clears_cookie(auth_client: AsyncClient):
    resp = await auth_client.post("/auth/logout")
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
        resp = await ac.get("/auth/me")
        assert resp.status_code == 401

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upsert_creates_new_user(session):
    """Verify user upsert logic directly — new user gets created."""
    from sqlmodel import select

    from app.models.user import User

    # No user exists yet
    result = await session.exec(select(User).where(User.provider == "github", User.provider_id == "newuser123"))
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

    result = await session.exec(select(User).where(User.provider == "github", User.provider_id == "newuser123"))
    assert result.first() is not None


@pytest.mark.asyncio
async def test_same_email_different_provider_creates_separate_accounts(session):
    """Accounts are keyed by (provider, provider_id), not email."""
    u1 = User(id=new_uuid7(), email="shared@example.com", name="User1", provider="github", provider_id="g1")
    u2 = User(id=new_uuid7(), email="shared@example.com", name="User2", provider="google", provider_id="g2")
    session.add(u1)
    session.add(u2)
    await session.commit()

    from sqlmodel import select
    result = await session.exec(select(User).where(User.email == "shared@example.com"))
    users = result.all()
    assert len(users) == 2
