from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FoodDetectionItem(BaseModel):
    name: str
    confidence: Optional[float] = None
    alternate_names: List[str] = Field(default_factory=list)
    suggested_portion_g: float = 100.0
    reasoning: Optional[str] = None


class VisionFoodResult(BaseModel):
    detected_foods: List[FoodDetectionItem] = Field(default_factory=list)
    primary_food: str
    confidence: Optional[float] = None
    alternate_names: List[str] = Field(default_factory=list)
    estimated_portion_g: float = 100.0
    notes: Optional[str] = None
    provider_used: str
    is_live_ai: bool = True


class FreshnessResult(BaseModel):
    food_category: str
    assessment_category: str  # "No obvious visual spoilage detected", "Visible quality concerns", "Potential spoilage indicators"
    confidence: Optional[float] = None
    visual_observations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    safety_disclaimer: str
    provider_used: str
    is_live_ai: bool = True


class FrameObservation(BaseModel):
    timestamp_s: float
    category: str  # Glove Usage, Hair Restraint, Surface Cleanliness, Cross-contamination
    observation: str
    severity: str  # Low, Medium, High
    confidence: Optional[float] = None


class HygieneAnalysisResult(BaseModel):
    overall_summary: str
    overall_risk_level: str  # Low, Moderate, High
    findings: List[FrameObservation] = Field(default_factory=list)
    practical_recommendations: List[str] = Field(default_factory=list)
    disclaimer: str
    provider_used: str
    is_live_ai: bool = True


class BaseAIProvider(ABC):
    @abstractmethod
    async def analyze_food_image(self, image_bytes: bytes, mime_type: str) -> VisionFoodResult:
        pass

    @abstractmethod
    async def analyze_freshness(self, image_bytes: bytes, mime_type: str, category: str) -> FreshnessResult:
        pass

    @abstractmethod
    async def analyze_hygiene_frames(self, frames: List[Dict[str, Any]]) -> HygieneAnalysisResult:
        pass

    @abstractmethod
    async def generate_recipe(
        self,
        query: str,
        ingredients: List[str],
        dietary_restrictions: List[str],
        cuisine: str,
        servings: int,
        cooking_time: Optional[int] = None
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def generate_meal_plan(
        self,
        dietary_pattern: str,
        allergies: List[str],
        restrictions: List[str],
        goal: str,
        cuisine_preferences: List[str],
        meals_per_day: int,
        days: int = 7
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], context: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def transcribe_audio(self, audio_bytes: bytes, mime_type: str) -> str:
        pass
