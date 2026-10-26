from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class RecipeGenerateRequest(BaseModel):
    query: str
    ingredients: List[str] = []
    dietary_restrictions: List[str] = []
    cuisine: str = "Global"
    servings: int = Field(default=2, ge=1, le=20)
    cooking_time_min: Optional[int] = 30
    skill_level: Optional[str] = "Beginner"


class RecipeChatRequest(BaseModel):
    message: str
    current_recipe: Optional[Dict[str, Any]] = None
    conversation_history: List[Dict[str, str]] = []


class SavedRecipeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    prep_time_min: int = 15
    cook_time_min: int = 20
    servings: int = 2
    cuisine: str = "Global"
    difficulty: str = "Easy"
    ingredients: List[Dict[str, Any]] = []
    instructions: List[str] = []
    substitutions: List[Dict[str, Any]] = []
    allergens: List[str] = []
    estimated_nutrition: Dict[str, Any] = {}
    food_safety_notes: Optional[str] = None


class RecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    description: Optional[str] = None
    prep_time_min: int
    cook_time_min: int
    servings: int
    cuisine: str
    difficulty: str
    ingredients: List[Dict[str, Any]]
    instructions: List[str]
    substitutions: List[Dict[str, Any]]
    allergens: List[str]
    estimated_nutrition: Dict[str, Any]
    food_safety_notes: Optional[str] = None
    created_at: datetime
