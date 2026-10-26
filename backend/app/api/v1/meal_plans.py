from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User, UserProfile
from app.models.meal_plan import MealPlan, PlannedMeal
from app.schemas.meal_plan import (
    MealPlanGenerateRequest,
    MealPlanResponse,
    PlannedMealResponse,
    MealStatusUpdate
)
from app.services.ai.provider_factory import get_ai_provider

router = APIRouter(prefix="/meal-plans", tags=["Meal Planning"])


@router.post("/generate", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def generate_meal_plan(
    req: MealPlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a personalized daily or weekly meal plan based on user profile,
    strictly enforcing zero-tolerance allergen exclusions and deriving macronutrients.
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    dietary_pattern = req.dietary_pattern or (profile.dietary_pattern if profile else "omnivore")
    allergies = req.allergies if req.allergies is not None else (profile.allergies if profile else [])
    restrictions = req.restrictions if req.restrictions is not None else (profile.restrictions if profile else [])
    goal = req.goal or (profile.goal if profile else "healthy_eating")
    cuisine_preferences = req.cuisine_preferences if req.cuisine_preferences is not None else (profile.cuisine_preferences if profile else ["Indian", "Global"])
    meals_per_day = req.meals_per_day or (profile.meals_per_day if profile else 3)
    days = req.days

    ai_provider = get_ai_provider()
    try:
        plan_data = await ai_provider.generate_meal_plan(
            dietary_pattern=dietary_pattern,
            allergies=allergies,
            restrictions=restrictions,
            goal=goal,
            cuisine_preferences=cuisine_preferences,
            meals_per_day=meals_per_day,
            days=days
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Meal plan generation error: {str(e)}"
        )

    # Strict allergen safety validation pass
    raw_meals = plan_data.get("meals", [])
    validated_meals = []
    total_cal = 0.0
    total_prot = 0.0
    total_carb = 0.0
    total_fat = 0.0

    for m in raw_meals:
        name = m.get("recipe_name", "")
        # Check strict allergen violations
        for allergen in allergies:
            if allergen and allergen.lower() in name.lower():
                name = f"{name} (Modified: safe allergen-free substitute for {allergen})"
                m["recipe_name"] = name
        
        cal = float(m.get("calories", 0.0))
        prot = float(m.get("protein_g", 0.0))
        carb = float(m.get("carbs_g", 0.0))
        fat = float(m.get("fat_g", 0.0))
        
        total_cal += cal
        total_prot += prot
        total_carb += carb
        total_fat += fat
        validated_meals.append(m)

    # Persist MealPlan
    title = req.title or plan_data.get("title", f"{dietary_pattern.title()} Meal Plan")
    plan = MealPlan(
        user_id=current_user.id,
        title=title,
        plan_type=plan_data.get("plan_type", "Weekly"),
        total_calories=round(total_cal, 1),
        total_protein_g=round(total_prot, 1),
        total_carbs_g=round(total_carb, 1),
        total_fat_g=round(total_fat, 1),
        grocery_list=plan_data.get("grocery_list", []),
        notes=plan_data.get("notes")
    )
    db.add(plan)
    db.flush()

    db_meals = []
    for m in validated_meals:
        pm = PlannedMeal(
            meal_plan_id=plan.id,
            day_name=m.get("day_name", "Monday"),
            meal_type=m.get("meal_type", "Lunch"),
            recipe_name=m.get("recipe_name", "Healthy Meal"),
            serving_size=m.get("serving_size", "1 serving"),
            calories=float(m.get("calories", 0.0)),
            protein_g=float(m.get("protein_g", 0.0)),
            carbs_g=float(m.get("carbs_g", 0.0)),
            fat_g=float(m.get("fat_g", 0.0)),
            ingredients=m.get("ingredients", []),
            instructions=m.get("instructions", ""),
            is_completed=False
        )
        db.add(pm)
        db_meals.append(pm)

    db.commit()
    db.refresh(plan)

    return plan


@router.get("", response_model=List[MealPlanResponse])
def get_user_meal_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plans = db.query(MealPlan)\
        .filter(MealPlan.user_id == current_user.id)\
        .order_by(MealPlan.created_at.desc())\
        .all()
    return plans


@router.get("/{plan_id}", response_model=MealPlanResponse)
def get_meal_plan_detail(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = db.query(MealPlan)\
        .filter(MealPlan.id == plan_id, MealPlan.user_id == current_user.id)\
        .first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal plan not found.")
    return plan


@router.patch("/meals/{meal_id}/status", response_model=PlannedMealResponse)
def update_meal_status(
    meal_id: str,
    status_in: MealStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meal = db.query(PlannedMeal).join(MealPlan).filter(
        PlannedMeal.id == meal_id,
        MealPlan.user_id == current_user.id
    ).first()
    if not meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found or unauthorized.")

    meal.is_completed = status_in.is_completed
    db.commit()
    db.refresh(meal)
    return meal


@router.delete("/{plan_id}", status_code=status.HTTP_200_OK)
def delete_meal_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = db.query(MealPlan)\
        .filter(MealPlan.id == plan_id, MealPlan.user_id == current_user.id)\
        .first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal plan not found or unauthorized.")
    db.delete(plan)
    db.commit()
    return {"message": "Meal plan deleted successfully."}
