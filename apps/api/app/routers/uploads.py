import hashlib
import logging
import time
from typing import Annotated

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import settings
from app.deps import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uploads", tags=["uploads"])


def _configure_cloudinary() -> None:
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
    )


async def _destroy_cloudinary_image(public_id: str) -> None:
    import asyncio

    _configure_cloudinary()
    try:
        await asyncio.to_thread(cloudinary.uploader.destroy, public_id)
    except Exception:
        logger.exception("Failed to destroy Cloudinary asset %s", public_id)


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
