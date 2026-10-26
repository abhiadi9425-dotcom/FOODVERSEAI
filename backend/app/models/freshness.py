import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, JSON, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class FreshnessAssessment(Base):
    __tablename__ = "freshness_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    image_url = Column(String(500), nullable=False)
    food_category = Column(String(100), nullable=False)
    
    # "No obvious visual spoilage detected", "Visible quality concerns", "Potential spoilage indicators"
    assessment_category = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=True)
    
    visual_observations = Column(JSON, default=list)  # Discoloration, bruising, mold patterns, texture
    recommendations = Column(JSON, default=list)  # Suggested next steps, storage advice
    safety_disclaimer = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="freshness_assessments")
