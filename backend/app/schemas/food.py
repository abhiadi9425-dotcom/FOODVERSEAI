from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class FoodAnalysisRequest(BaseModel):
    food_name: str
    serving_size_g: float = Field(default=100.0, ge=1.0, le=5000.0)
    serving_unit: str = "grams"
    image_url: Optional[str] = None


class FoodAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[str] = None
    food_name: str
    alternate_names: List[str] = []
    confidence: Optional[float] = None
    serving_size_g: float
    serving_unit: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sugar_g: float
    sodium_mg: float
    micronutrients: Dict[str, Any] = {}
    data_source: str
    is_estimate: bool
    notes: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None


class RecalculateRequest(BaseModel):
    food_name: str
    serving_size_g: float
    serving_unit: str = "grams"
