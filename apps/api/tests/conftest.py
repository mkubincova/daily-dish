import os

# Set required env vars before any app imports
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

import app.models  # noqa: F401 — ensure models are registered
from app.database import get_session
from app.deps import SESSION_COOKIE, _get_serializer
from app.main import app
from app.models.user import User
from app.utils.uuid7 import new_uuid7

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def session():
    async with TestSessionLocal() as s:
        yield s


@pytest_asyncio.fixture
async def client(session: AsyncSession):
    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user(session: AsyncSession) -> User:
    u = User(
        id=new_uuid7(),
        email="test@example.com",
        name="Test User",
        avatar_url="https://example.com/avatar.png",
        provider="github",
        provider_id="12345",
    )
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


@pytest_asyncio.fixture
async def other_user(session: AsyncSession) -> User:
    u = User(
        id=new_uuid7(),
        email="other@example.com",
        name="Other User",
        avatar_url=None,
        provider="github",
        provider_id="99999",
    )
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


def make_session_cookie(user_id: str) -> str:
    return _get_serializer().dumps({"user_id": user_id})


@pytest_asyncio.fixture
async def auth_client(session: AsyncSession, user: User):
    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    cookie = make_session_cookie(user.id)
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies={SESSION_COOKIE: cookie},
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
