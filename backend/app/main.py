import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import Base, engine
# Import all models to ensure registration with SQLAlchemy Base
import app.models  # noqa: F401

from app.api.v1.auth import router as auth_router
from app.api.v1.profile import router as profile_router
from app.api.v1.food import router as food_router
from app.api.v1.freshness import router as freshness_router
from app.api.v1.hygiene import router as hygiene_router
from app.api.v1.cooking import router as cooking_router
from app.api.v1.meal_plans import router as meal_plans_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.health import router as health_router

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FoodVerse AI — Multimodal Food Intelligence API",
    description=(
        "Production-ready multimodal food intelligence platform combining computer vision, "
        "speech-to-text, large language model reasoning, verified USDA nutritional calculations, "
        "food freshness assessment, kitchen hygiene auditing, and personalized meal planning."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists and mount static route
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "frames"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include API v1 Routers
api_v1_prefix = settings.API_V1_STR
app.include_router(health_router, prefix=api_v1_prefix)
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(profile_router, prefix=api_v1_prefix)
app.include_router(food_router, prefix=api_v1_prefix)
app.include_router(freshness_router, prefix=api_v1_prefix)
app.include_router(hygiene_router, prefix=api_v1_prefix)
app.include_router(cooking_router, prefix=api_v1_prefix)
app.include_router(meal_plans_router, prefix=api_v1_prefix)
app.include_router(assistant_router, prefix=api_v1_prefix)


@app.get("/")
def root():
    return {
        "service": "FoodVerse AI — Multimodal Food Intelligence Platform",
        "documentation": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "status": "operational"
    }
