from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.middleware import ForwardedHostMiddleware
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
    same_site="lax",
    https_only=settings.environment == "production",
)

app.add_middleware(
    CORSMiddleware,
    # Production is same-origin via the Vercel proxy; only localhost origins needed for dev.
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Outermost: rewrite Host from X-Forwarded-Host before any handler builds a URL.
app.add_middleware(ForwardedHostMiddleware)

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(categories_router)
api_router.include_router(tags_router)
api_router.include_router(recipes_router)
api_router.include_router(favorites_router)
api_router.include_router(uploads_router)
app.include_router(api_router)


# Health check kept at root so Railway's health probe does not require the /api prefix.
@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}
