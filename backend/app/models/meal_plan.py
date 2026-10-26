import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    plan_type = Column(String(50), default="Weekly")  # Daily, Weekly
    start_date = Column(String(50), nullable=True)
    
    total_calories = Column(Float, default=0.0)
    total_protein_g = Column(Float, default=0.0)
    total_carbs_g = Column(Float, default=0.0)
    total_fat_g = Column(Float, default=0.0)
    
    grocery_list = Column(JSON, default=list)  # list of {"category": str, "items": [{"name": str, "quantity": str, "purchased": bool}]}
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="meal_plans")
    meals = relationship("PlannedMeal", back_populates="meal_plan", cascade="all, delete-orphan")


class PlannedMeal(Base):
    __tablename__ = "planned_meals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meal_plan_id = Column(String(36), ForeignKey("meal_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    
    day_name = Column(String(50), default="Monday")  # Monday, Tuesday, etc.
    meal_type = Column(String(50), default="Breakfast")  # Breakfast, Lunch, Dinner, Snack
    recipe_name = Column(String(255), nullable=False)
    serving_size = Column(String(100), default="1 serving")
    
    calories = Column(Float, default=0.0)
    protein_g = Column(Float, default=0.0)
    carbs_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)
    
    ingredients = Column(JSON, default=list)  # list of str or {"name": str, "qty": str}
    instructions = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)

    meal_plan = relationship("MealPlan", back_populates="meals")
