from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.favorites import router as favorites_router
from app.routers.recipes import router as recipes_router
from app.routers.tags import router as tags_router
from app.routers.uploads import router as uploads_router

app = FastAPI(
    title="Daily Dish API",
    description="Personal recipe app API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    same_site="none" if settings.environment == "production" else "lax",
    https_only=settings.environment == "production",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(recipes_router)
app.include_router(favorites_router)
app.include_router(uploads_router)


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}
