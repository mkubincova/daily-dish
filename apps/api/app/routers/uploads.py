import hashlib
import time
from typing import Annotated

import cloudinary
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import settings
from app.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/uploads", tags=["uploads"])


def _configure_cloudinary() -> None:
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
    )


class SignedUploadParams(BaseModel):
    cloud_name: str
    api_key: str
    timestamp: int
    signature: str
    folder: str


@router.post("/sign", response_model=SignedUploadParams)
async def sign_upload(
    current_user: Annotated[User, Depends(get_current_user)],
) -> SignedUploadParams:
    _configure_cloudinary()
    timestamp = int(time.time())
    folder = "daily-dish/recipes"
    params_to_sign = f"folder={folder}&timestamp={timestamp}"
    signature = hashlib.sha1(
        f"{params_to_sign}{settings.cloudinary_api_secret}".encode()
    ).hexdigest()

    return SignedUploadParams(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        timestamp=timestamp,
        signature=signature,
        folder=folder,
    )
