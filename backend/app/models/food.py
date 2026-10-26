import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class FoodAnalysis(Base):
    __tablename__ = "food_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    image_url = Column(String(500), nullable=True)
    food_name = Column(String(255), nullable=False)
    alternate_names = Column(JSON, default=list)
    confidence = Column(Float, nullable=True)
    
    serving_size_g = Column(Float, default=100.0)
    serving_unit = Column(String(50), default="grams")
    
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, default=0.0)
    carbs_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)
    fiber_g = Column(Float, default=0.0)
    sugar_g = Column(Float, default=0.0)
    sodium_mg = Column(Float, default=0.0)
    
    micronutrients = Column(JSON, default=dict)
    data_source = Column(String(100), default="USDA Reference Database")
    is_estimate = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="food_analyses")
