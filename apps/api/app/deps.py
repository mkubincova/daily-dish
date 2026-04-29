from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Response, status
from itsdangerous import BadSignature, URLSafeSerializer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.database import get_session
from app.models.user import User


def _get_serializer() -> URLSafeSerializer:
    return URLSafeSerializer(settings.secret_key, salt="session")


SESSION_COOKIE = "auth_token"


def set_session_cookie(response: Response, user_id: str) -> None:
    s = _get_serializer()
    token = s.dumps({"user_id": user_id})
    is_prod = settings.environment == "production"
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,  # 30 days
    )


def clear_session_cookie(response: Response) -> None:
    is_prod = settings.environment == "production"
    response.delete_cookie(
        key=SESSION_COOKIE,
        httponly=True,
        secure=is_prod,
        samesite="lax",
    )


def _decode_session(token: str) -> str | None:
    try:
        data = _get_serializer().loads(token)
        return data["user_id"]
    except (BadSignature, KeyError):
        return None


async def get_current_user_optional(
    session: Annotated[AsyncSession, Depends(get_session)],
    session_cookie: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> User | None:
    if not session_cookie:
        return None
    user_id = _decode_session(session_cookie)
    if not user_id:
        return None
    user = await session.get(User, user_id)
    return user


async def get_current_user(
    user: Annotated[User | None, Depends(get_current_user_optional)],
) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
