from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_user_optional
from app.models.user import User
from app.models.freshness import FreshnessAssessment
from app.schemas.freshness import FreshnessResponse
from app.services.ai.provider_factory import get_ai_provider
from app.utils.file_validation import validate_image_upload, save_upload_safely, IMAGE_MAX_SIZE

router = APIRouter(prefix="/freshness", tags=["Freshness Assessment"])


@router.post("/analyze", response_model=FreshnessResponse)
async def analyze_freshness(
    image: UploadFile = File(...),
    food_category: str = Form("Fresh Produce / Fruits"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Evaluates visible freshness, discoloration, and mold-like patterns on food images.
    Distinguishes visual surface assessment from microbiological safety guarantees.
    """
    mime_type = validate_image_upload(image)
    _, image_bytes, relative_image_url = await save_upload_safely(
        image, max_bytes=IMAGE_MAX_SIZE, prefix="freshness"
    )

    ai_provider = get_ai_provider()
    try:
        freshness_result = await ai_provider.analyze_freshness(
            image_bytes=image_bytes,
            mime_type=mime_type,
            category=food_category
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Freshness analysis failure: {str(e)}"
        )

    record_id = None
    if current_user:
        assessment = FreshnessAssessment(
            user_id=current_user.id,
            image_url=relative_image_url,
            food_category=freshness_result.food_category,
            assessment_category=freshness_result.assessment_category,
            confidence=freshness_result.confidence,
            visual_observations=freshness_result.visual_observations,
            recommendations=freshness_result.recommendations,
            safety_disclaimer=freshness_result.safety_disclaimer
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        record_id = assessment.id

    return FreshnessResponse(
        id=record_id,
        image_url=relative_image_url,
        food_category=freshness_result.food_category,
        assessment_category=freshness_result.assessment_category,
        confidence=freshness_result.confidence,
        visual_observations=freshness_result.visual_observations,
        recommendations=freshness_result.recommendations,
        safety_disclaimer=freshness_result.safety_disclaimer,
        provider_used=freshness_result.provider_used,
        is_live_ai=freshness_result.is_live_ai
    )


@router.get("/history", response_model=List[FreshnessResponse])
def get_freshness_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(FreshnessAssessment)\
        .filter(FreshnessAssessment.user_id == current_user.id)\
        .order_by(FreshnessAssessment.created_at.desc())\
        .all()
    return records
