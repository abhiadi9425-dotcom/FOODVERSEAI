from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class HygieneFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[str] = None
    timestamp_s: float
    category: str
    observation: str
    severity: str
    confidence: Optional[float] = None
    frame_image_url: Optional[str] = None


class HygieneReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[str] = None
    video_url: str
    video_duration_s: Optional[float] = None
    total_frames_analyzed: int
    overall_summary: str
    overall_risk_level: str
    findings: List[HygieneFindingResponse] = []
    practical_recommendations: List[str] = []
    disclaimer: str
    created_at: Optional[datetime] = None
