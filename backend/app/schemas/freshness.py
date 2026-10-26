from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class FreshnessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[str] = None
    image_url: str
    food_category: str
    assessment_category: str  # "No obvious visual spoilage detected", "Visible quality concerns", "Potential spoilage indicators"
    confidence: Optional[float] = None
    visual_observations: List[str]
    recommendations: List[str]
    safety_disclaimer: str
    provider_used: str
    is_live_ai: bool
    created_at: Optional[datetime] = None
