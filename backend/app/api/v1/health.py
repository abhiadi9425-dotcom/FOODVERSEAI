from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.deps import get_db
from app.services.ai.provider_factory import get_provider_status

router = APIRouter(tags=["System"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    ai_status = get_provider_status()

    return {
        "status": "healthy" if db_ok else "degraded",
        "database_connected": db_ok,
        "ai_providers": ai_status,
        "version": "1.0.0",
        "service": "FoodVerse AI Backend"
    }
