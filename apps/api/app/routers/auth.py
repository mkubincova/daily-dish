from datetime import UTC, datetime
from typing import Annotated

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.database import get_session
from app.deps import clear_session_cookie, get_current_user, set_session_cookie
from app.models.user import User
from app.utils.uuid7 import new_uuid7

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()

oauth.register(
    name="github",
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)

oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


class UserPublic(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: str | None
    provider: str


@router.get("/{provider}/login")
async def oauth_login(provider: str, request: Request) -> Response:
    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=404, detail="Unknown provider")
    redirect_uri = str(request.url_for("oauth_callback", provider=provider))
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Response:
    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=404, detail="Unknown provider")

    # Handle user-denied authorization
    if request.query_params.get("error"):
        return Response(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": f"{settings.frontend_url}?auth_error=cancelled"},
        )

    token = await client.authorize_access_token(request)

    if provider == "github":
        resp = await client.get("user", token=token)
        profile = resp.json()
        email_resp = await client.get("user/emails", token=token)
        emails = email_resp.json()
        primary = next((e["email"] for e in emails if e["primary"]), profile.get("email", ""))
        provider_id = str(profile["id"])
        name = profile.get("name") or profile.get("login") or ""
        avatar_url = profile.get("avatar_url")
        email = primary
    elif provider == "google":
        userinfo = token.get("userinfo") or await client.userinfo(token=token)
        provider_id = userinfo["sub"]
        email = userinfo.get("email", "")
        name = userinfo.get("name", "")
        avatar_url = userinfo.get("picture")
    else:
        raise HTTPException(status_code=404, detail="Unknown provider")

    stmt = select(User).where(User.provider == provider, User.provider_id == provider_id)
    result = await session.exec(stmt)
    user = result.first()

    if user is None:
        user = User(
            id=new_uuid7(),
            email=email,
            name=name,
            avatar_url=avatar_url,
            provider=provider,
            provider_id=provider_id,
        )
        session.add(user)
    else:
        user.name = name
        user.avatar_url = avatar_url
        user.updated_at = datetime.now(UTC)
        session.add(user)

    await session.commit()
    await session.refresh(user)

    redirect = Response(
        status_code=status.HTTP_302_FOUND,
        headers={"Location": settings.frontend_url},
    )
    set_session_cookie(redirect, user.id)
    return redirect


@router.get("/me", response_model=UserPublic)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserPublic:
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        provider=current_user.provider,
    )


@router.post("/logout")
async def logout(response: Response) -> dict:
    clear_session_cookie(response)
    return {"message": "Logged out"}


class TestLoginIn(BaseModel):
    email: str
    name: str = "Test User"


@router.post("/_test/login", include_in_schema=False)
async def test_login(
    body: TestLoginIn,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserPublic:
    # Test-only shortcut for Playwright/E2E. Refuse to load in production.
    if settings.environment == "production":
        raise HTTPException(status_code=404, detail="Not found")

    stmt = select(User).where(User.provider == "test", User.email == body.email)
    result = await session.exec(stmt)
    user = result.first()

    if user is None:
        user = User(
            id=new_uuid7(),
            email=body.email,
            name=body.name,
            avatar_url=None,
            provider="test",
            provider_id=body.email,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    set_session_cookie(response, user.id)
    return UserPublic(
        id=user.id,
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        provider=user.provider,
    )
