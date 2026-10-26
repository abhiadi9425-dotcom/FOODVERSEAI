import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class SavedRecipe(Base):
    __tablename__ = "saved_recipes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    prep_time_min = Column(Integer, default=15)
    cook_time_min = Column(Integer, default=20)
    servings = Column(Integer, default=2)
    cuisine = Column(String(100), default="Global")
    difficulty = Column(String(50), default="Easy")
    
    ingredients = Column(JSON, default=list)  # list of {"item": str, "quantity": str, "checked": bool}
    instructions = Column(JSON, default=list)  # list of str
    substitutions = Column(JSON, default=list)  # list of {"original": str, "alternative": str, "reason": str}
    allergens = Column(JSON, default=list)  # list of allergen names
    estimated_nutrition = Column(JSON, default=dict)  # {"calories": int, "protein_g": float, ...}
    food_safety_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="saved_recipes")
