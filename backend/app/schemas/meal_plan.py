from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class MealPlanGenerateRequest(BaseModel):
    title: Optional[str] = None
    plan_type: str = "Weekly"  # Daily or Weekly
    days: int = Field(default=7, ge=1, le=7)
    meals_per_day: int = Field(default=3, ge=1, le=5)
    dietary_pattern: Optional[str] = None  # if not specified, loaded from user profile
    allergies: Optional[List[str]] = None
    restrictions: Optional[List[str]] = None
    goal: Optional[str] = None
    cuisine_preferences: Optional[List[str]] = None


class PlannedMealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    meal_plan_id: str
    day_name: str
    meal_type: str
    recipe_name: str
    serving_size: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    ingredients: List[Any] = []
    instructions: Optional[str] = None
    is_completed: bool


class MealPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    title: str
    plan_type: str
    start_date: Optional[str] = None
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    grocery_list: List[Dict[str, Any]] = []
    notes: Optional[str] = None
    meals: List[PlannedMealResponse] = []
    created_at: datetime


class MealStatusUpdate(BaseModel):
    is_completed: bool
