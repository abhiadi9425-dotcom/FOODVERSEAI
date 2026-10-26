from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ProfileUpdate(BaseModel):
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = "moderate"
    dietary_pattern: Optional[str] = "omnivore"
    allergies: Optional[List[str]] = []
    restrictions: Optional[List[str]] = []
    goal: Optional[str] = "maintenance"
    cuisine_preferences: Optional[List[str]] = []
    budget_range: Optional[str] = "moderate"
    meals_per_day: Optional[int] = 3
    preferred_foods: Optional[List[str]] = []
    avoided_foods: Optional[List[str]] = []


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: str
    dietary_pattern: str
    allergies: List[str]
    restrictions: List[str]
    goal: str
    cuisine_preferences: List[str]
    budget_range: str
    meals_per_day: int
    preferred_foods: List[str]
    avoided_foods: List[str]
    updated_at: datetime
