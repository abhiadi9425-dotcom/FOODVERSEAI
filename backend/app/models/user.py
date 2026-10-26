import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    food_analyses = relationship("FoodAnalysis", back_populates="user", cascade="all, delete-orphan")
    freshness_assessments = relationship("FreshnessAssessment", back_populates="user", cascade="all, delete-orphan")
    hygiene_reports = relationship("HygieneReport", back_populates="user", cascade="all, delete-orphan")
    saved_recipes = relationship("SavedRecipe", back_populates="user", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    age = Column(Integer, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    activity_level = Column(String(50), default="moderate")  # sedentary, light, moderate, active, very_active
    
    dietary_pattern = Column(String(50), default="omnivore")  # omnivore, vegetarian, vegan, pescatarian, keto, paleo, sattvic
    allergies = Column(JSON, default=list)  # ["peanuts", "dairy", "gluten", ...]
    restrictions = Column(JSON, default=list)  # ["halal", "kosher", "low-sodium", ...]
    goal = Column(String(50), default="maintenance")  # weight_loss, muscle_gain, maintenance, healthy_eating, diabetic_friendly
    cuisine_preferences = Column(JSON, default=list)  # ["Indian", "Mediterranean", "Mexican", ...]
    budget_range = Column(String(50), default="moderate")  # budget, moderate, premium
    meals_per_day = Column(Integer, default=3)
    preferred_foods = Column(JSON, default=list)
    avoided_foods = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")
