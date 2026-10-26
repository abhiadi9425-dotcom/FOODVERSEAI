from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_user_optional
from app.models.user import User
from app.models.food import FoodAnalysis
from app.schemas.food import FoodAnalysisResponse, RecalculateRequest
from app.services.ai.provider_factory import get_ai_provider
from app.services.nutrition.calculator import NutritionCalculator
from app.services.nutrition.usda_data import VERIFIED_FOOD_DATABASE
from app.utils.file_validation import validate_image_upload, save_upload_safely, IMAGE_MAX_SIZE

router = APIRouter(prefix="/food", tags=["Food Analysis"])


@router.get("/database-items")
def get_verified_database_items():
    """
    Returns list of verified laboratory benchmark food items for instant selection or autocomplete.
    """
    items = []
    for key, val in VERIFIED_FOOD_DATABASE.items():
        items.append({
            "key": key,
            "name": val["canonical_name"],
            "category": val.get("category", "General"),
            "default_serving_g": val.get("default_serving_g", 100),
            "serving_description": val.get("serving_description", "1 serving"),
            "calories_per_100g": val["per_100g"]["calories"],
            "allergens": val.get("allergens", []),
            "source": val.get("source", "USDA FoodData Central")
        })
    return items


@router.post("/recalculate", response_model=dict)
def recalculate_nutrition(req: RecalculateRequest):
    """
    Deterministically rescales nutrition when the user adjusts serving size (grams).
    """
    return NutritionCalculator.calculate_scaled_nutrition(
        food_name=req.food_name,
        serving_size_g=req.serving_size_g,
        serving_unit=req.serving_unit
    )


@router.post("/analyze", response_model=FoodAnalysisResponse)
async def analyze_food(
    image: Optional[UploadFile] = File(None),
    food_name: Optional[str] = Form(None),
    serving_size_g: Optional[float] = Form(100.0),
    serving_unit: Optional[str] = Form("grams"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Processes either an uploaded image via vision AI or a manually entered/selected food dish.
    Calculates verified USDA / laboratory nutritional values scaled to serving grams.
    Saves analysis to user history if authenticated.
    """
    relative_image_url = None
    detected_primary = food_name
    detected_alternates = []
    confidence = None
    notes = None

    if image and image.filename:
        mime_type = validate_image_upload(image)
        _, image_bytes, relative_image_url = await save_upload_safely(
            image, max_bytes=IMAGE_MAX_SIZE, prefix="food"
        )
        ai_provider = get_ai_provider()
        try:
            vision_result = await ai_provider.analyze_food_image(image_bytes, mime_type)
            if not detected_primary:
                detected_primary = vision_result.primary_food
            detected_alternates = vision_result.alternate_names
            confidence = vision_result.confidence
            notes = vision_result.notes
            if not serving_size_g or serving_size_g == 100.0:
                serving_size_g = vision_result.estimated_portion_g
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Vision analysis error: {str(e)}"
            )

    if not detected_primary:
        detected_primary = "Mixed Prepared Dish"

    nutrition_data = NutritionCalculator.calculate_scaled_nutrition(
        food_name=detected_primary,
        serving_size_g=serving_size_g or 100.0,
        serving_unit=serving_unit or "grams"
    )

    # Use the recognized dish name as the display title, with reference database match in alternates
    display_food_name = detected_primary if detected_primary != "Mixed Prepared Dish" else nutrition_data["food_name"]
    if nutrition_data["food_name"] != display_food_name and nutrition_data["food_name"] not in detected_alternates:
        detected_alternates = [f"Ref: {nutrition_data['food_name']}"] + detected_alternates

    # Persist record if user is authenticated
    record_id = None
    if current_user:
        analysis_record = FoodAnalysis(
            user_id=current_user.id,
            image_url=relative_image_url,
            food_name=display_food_name,
            alternate_names=detected_alternates,
            confidence=confidence,
            serving_size_g=nutrition_data["serving_size_g"],
            serving_unit=nutrition_data["serving_unit"],
            calories=nutrition_data["calories"],
            protein_g=nutrition_data["protein_g"],
            carbs_g=nutrition_data["carbs_g"],
            fat_g=nutrition_data["fat_g"],
            fiber_g=nutrition_data["fiber_g"],
            sugar_g=nutrition_data["sugar_g"],
            sodium_mg=nutrition_data["sodium_mg"],
            micronutrients=nutrition_data.get("micronutrients", {}),
            data_source=nutrition_data.get("data_source", "USDA Reference Database"),
            is_estimate=nutrition_data.get("is_estimate", False),
            notes=notes or nutrition_data.get("uncertainty_note")
        )
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)
        record_id = analysis_record.id

    return FoodAnalysisResponse(
        id=record_id,
        food_name=display_food_name,
        alternate_names=detected_alternates,
        confidence=confidence,
        serving_size_g=nutrition_data["serving_size_g"],
        serving_unit=nutrition_data["serving_unit"],
        calories=nutrition_data["calories"],
        protein_g=nutrition_data["protein_g"],
        carbs_g=nutrition_data["carbs_g"],
        fat_g=nutrition_data["fat_g"],
        fiber_g=nutrition_data["fiber_g"],
        sugar_g=nutrition_data["sugar_g"],
        sodium_mg=nutrition_data["sodium_mg"],
        micronutrients=nutrition_data.get("micronutrients", {}),
        data_source=nutrition_data.get("data_source", "USDA Reference Database"),
        is_estimate=nutrition_data.get("is_estimate", False),
        notes=notes or nutrition_data.get("uncertainty_note"),
        image_url=relative_image_url
    )


@router.get("/history", response_model=List[FoodAnalysisResponse])
def get_food_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns user's private food analyses, strictly isolated by user_id.
    """
    records = db.query(FoodAnalysis)\
        .filter(FoodAnalysis.user_id == current_user.id)\
        .order_by(FoodAnalysis.created_at.desc())\
        .all()
    return records


@router.get("/history/{analysis_id}", response_model=FoodAnalysisResponse)
def get_food_analysis_detail(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(FoodAnalysis)\
        .filter(FoodAnalysis.id == analysis_id, FoodAnalysis.user_id == current_user.id)\
        .first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food analysis record not found.")
    return record


@router.delete("/history/{analysis_id}", status_code=status.HTTP_200_OK)
def delete_food_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(FoodAnalysis)\
        .filter(FoodAnalysis.id == analysis_id, FoodAnalysis.user_id == current_user.id)\
        .first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found or unauthorized.")
    db.delete(record)
    db.commit()
    return {"message": "Food analysis record deleted successfully."}
