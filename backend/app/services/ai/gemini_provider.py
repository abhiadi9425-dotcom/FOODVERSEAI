import json
import logging
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from app.services.ai.base import (
    BaseAIProvider,
    VisionFoodResult,
    FoodDetectionItem,
    FreshnessResult,
    HygieneAnalysisResult,
    FrameObservation,
)

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

    async def analyze_food_image(self, image_bytes: bytes, mime_type: str) -> VisionFoodResult:
        prompt = """
You are a food recognition AI. Analyze this image and identify the food items present.
Return a STRICT JSON object with this exact structure:
{
  "detected_foods": [
    {
      "name": "Food item name",
      "confidence": 0.95,
      "alternate_names": ["synonym 1", "synonym 2"],
      "suggested_portion_g": 200,
      "reasoning": "Visible texture and preparation style"
    }
  ],
  "primary_food": "Most prominent food item",
  "confidence": 0.92,
  "alternate_names": ["alternate 1"],
  "estimated_portion_g": 200,
  "notes": "Estimated portion based on standard plate serving. Visual analysis cannot guarantee exact portion weight."
}
Only return valid JSON. Do not wrap in markdown or backticks.
"""
        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            raw = response.text.strip()
            data = json.loads(raw)
            detected = [
                FoodDetectionItem(
                    name=item.get("name", "Unknown Food"),
                    confidence=item.get("confidence"),
                    alternate_names=item.get("alternate_names", []),
                    suggested_portion_g=float(item.get("suggested_portion_g", 100)),
                    reasoning=item.get("reasoning")
                )
                for item in data.get("detected_foods", [])
            ]
            return VisionFoodResult(
                detected_foods=detected,
                primary_food=data.get("primary_food", "Recognized Food Item"),
                confidence=data.get("confidence"),
                alternate_names=data.get("alternate_names", []),
                estimated_portion_g=float(data.get("estimated_portion_g", 150)),
                notes=data.get("notes"),
                provider_used=f"Google Gemini ({self.model_name})",
                is_live_ai=True
            )
        except Exception as e:
            logger.error(f"Gemini food vision error: {e}")
            raise e

    async def analyze_freshness(self, image_bytes: bytes, mime_type: str, category: str) -> FreshnessResult:
        prompt = f"""
You are a food freshness and visible spoilage assessment AI.
The user specifies this food category: "{category}".
Examine the visible exterior: discoloration, spots, mold-like mycelium, wilting, surface texture changes, bruising, or slime.
IMPORTANT SAFETY DIRECTIVE:
Visual appearance alone CANNOT establish that food is microbiologically safe. Pathogens (e.g. Salmonella, Listeria, toxin-producing bacteria) can multiply without visible signs. Never guarantee that food is safe to consume.
Return STRICT JSON:
{{
  "assessment_category": "No obvious visual spoilage detected" OR "Visible quality concerns" OR "Potential spoilage indicators",
  "confidence": 0.88,
  "visual_observations": [
    "Specific observable detail 1",
    "Specific observable detail 2"
  ],
  "recommendations": [
    "Actionable guidance 1",
    "Proper storage advice 2"
  ],
  "safety_disclaimer": "Visual assessment is for guidance only and cannot detect microscopic bacteria, toxins, or internal decay. When in doubt, follow government food safety standards and discard questionable items."
}}
Only return valid JSON.
"""
        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text.strip())
            return FreshnessResult(
                food_category=category,
                assessment_category=data.get("assessment_category", "Visible quality concerns"),
                confidence=data.get("confidence"),
                visual_observations=data.get("visual_observations", ["Visual surface evaluated"]),
                recommendations=data.get("recommendations", ["Store at appropriate temperatures"]),
                safety_disclaimer=data.get(
                    "safety_disclaimer",
                    "Visual assessment cannot guarantee microbiological safety. Follow standard food safety rules."
                ),
                provider_used=f"Google Gemini ({self.model_name})",
                is_live_ai=True
            )
        except Exception as e:
            logger.error(f"Gemini freshness error: {e}")
            raise e

    async def analyze_hygiene_frames(self, frames: List[Dict[str, Any]]) -> HygieneAnalysisResult:
        """
        Takes sampled frames with timestamp_s and image_bytes.
        """
        parts = []
        for i, f in enumerate(frames[:6]):  # sample up to 6 frames
            parts.append(f"Frame {i+1} at timestamp {f['timestamp_s']:.1f}s:")
            parts.append(types.Part.from_bytes(data=f["image_bytes"], mime_type="image/jpeg"))

        prompt = """
You are an expert commercial kitchen hygiene and food handling analyst.
Inspect these extracted video frames.
Evaluate visible indicators:
- Glove usage where raw or ready-to-eat foods are handled
- Hair restraints / hairnets / beard nets
- Cleanliness of food contact surfaces and cutting boards
- Visible cross-contamination risks (e.g. raw poultry near ready produce)
- Food separation and storage hygiene
IMPORTANT:
Clearly identify this as an AI-assisted preliminary observation based on sampled frames, NOT an official regulatory or health inspection certification.
Return STRICT JSON:
{
  "overall_summary": "Concise summary of overall visible hygiene practices across frames.",
  "overall_risk_level": "Low" OR "Moderate" OR "High",
  "findings": [
    {
      "timestamp_s": 2.5,
      "category": "Glove Usage",
      "observation": "Food handler observed wearing disposable food-grade gloves while plating.",
      "severity": "Low",
      "confidence": 0.90
    }
  ],
  "practical_recommendations": [
    "Practical corrective recommendation 1",
    "Guidance 2"
  ],
  "disclaimer": "This is an AI-assisted visual overview from sampled video frames and does not constitute a legally binding health inspection, regulatory audit, or sanitization certificate."
}
Only return valid JSON.
"""
        parts.append(prompt)
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=parts,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text.strip())
            findings = [
                FrameObservation(
                    timestamp_s=float(item.get("timestamp_s", 0.0)),
                    category=item.get("category", "Cleanliness"),
                    observation=item.get("observation", "Observed frame behavior"),
                    severity=item.get("severity", "Low"),
                    confidence=item.get("confidence")
                )
                for item in data.get("findings", [])
            ]
            return HygieneAnalysisResult(
                overall_summary=data.get("overall_summary", "Preliminary kitchen visual hygiene assessment."),
                overall_risk_level=data.get("overall_risk_level", "Moderate"),
                findings=findings,
                practical_recommendations=data.get("practical_recommendations", []),
                disclaimer=data.get(
                    "disclaimer",
                    "This report is an automated preliminary observation, not an official inspection."
                ),
                provider_used=f"Google Gemini ({self.model_name})",
                is_live_ai=True
            )
        except Exception as e:
            logger.error(f"Gemini hygiene error: {e}")
            raise e

    async def generate_recipe(
        self,
        query: str,
        ingredients: List[str],
        dietary_restrictions: List[str],
        cuisine: str,
        servings: int,
        cooking_time: Optional[int] = None
    ) -> Dict[str, Any]:
        prompt = f"""
You are an expert chef and culinary scientist.
User Request: {query}
Available Ingredients: {', '.join(ingredients) if ingredients else 'Any standard pantry staples'}
Dietary Restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
Cuisine Preference: {cuisine}
Servings: {servings}
Cooking Time: {cooking_time or 30} minutes

Create an authentic, delicious, step-by-step recipe.
Support regional nuances (especially Indian spices, authentic terminology like tadka, bhunao, tempering, or global culinary methods).
Derive accurate estimated ingredients with gram measurements.
Return STRICT JSON:
{{
  "title": "Recipe Title",
  "description": "Appetizing description of the dish",
  "prep_time_min": 15,
  "cook_time_min": 20,
  "servings": {servings},
  "cuisine": "{cuisine}",
  "difficulty": "Easy",
  "ingredients": [
    {{"item": "Basmati rice", "quantity": "150g", "checked": false}},
    {{"item": "Cumin seeds (Jeera)", "quantity": "1 tsp (3g)", "checked": false}}
  ],
  "instructions": [
    "Step 1: Rinse rice thoroughly until water runs clear...",
    "Step 2: Heat ghee in a heavy-bottomed pot and add cumin seeds..."
  ],
  "substitutions": [
    {{"original": "Ghee", "alternative": "Coconut oil or neutral vegetable oil", "reason": "Vegan alternative"}}
  ],
  "allergens": ["dairy"],
  "estimated_nutrition": {{
    "calories_per_serving": 320,
    "protein_g": 8.5,
    "carbs_g": 48.0,
    "fat_g": 9.0,
    "fiber_g": 3.2
  }},
  "food_safety_notes": "Ensure ingredients reach internal cooking temperatures; store leftovers in an airtight container under 4°C within 2 hours."
}}
Only return valid JSON.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text.strip())
        except Exception as e:
            logger.error(f"Gemini recipe error: {e}")
            raise e

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
        prompt = f"""
You are a precision clinical and sports nutritionist.
Plan: {days} Days.
Dietary Pattern: {dietary_pattern}
STRICT ALLERGIES (MUST EXCLUDE ENTIRELY): {', '.join(allergies) if allergies else 'None'}
Restrictions: {', '.join(restrictions) if restrictions else 'None'}
Primary Goal: {goal}
Cuisines: {', '.join(cuisine_preferences) if cuisine_preferences else 'Varied'}
Meals per Day: {meals_per_day}

CRITICAL SAFETY DIRECTIVE:
Treat allergies as zero-tolerance absolute exclusions.
Return STRICT JSON:
{{
  "title": "{dietary_pattern.title()} Balanced Plan for {goal.replace('_', ' ').title()}",
  "plan_type": "{'Weekly' if days > 1 else 'Daily'}",
  "total_daily_averages": {{
    "calories": 1950,
    "protein_g": 110,
    "carbs_g": 210,
    "fat_g": 65
  }},
  "grocery_list": [
    {{
      "category": "Produce",
      "items": [{{"name": "Baby Spinach", "quantity": "500g", "purchased": false}}]
    }},
    {{
      "category": "Pantry & Grains",
      "items": [{{"name": "Whole Wheat Atta / Flour", "quantity": "1kg", "purchased": false}}]
    }}
  ],
  "meals": [
    {{
      "day_name": "Monday",
      "meal_type": "Breakfast",
      "recipe_name": "Vegetable Poha with Roasted Peanuts (or seeds if allergic)",
      "serving_size": "1 bowl (250g)",
      "calories": 350,
      "protein_g": 7.0,
      "carbs_g": 62.0,
      "fat_g": 8.0,
      "ingredients": ["Flattened rice 100g", "Onion 50g", "Peas 30g", "Mustard seeds 3g"],
      "instructions": "Rinse poha, temper mustard seeds and curry leaves in oil, saute onions and vegetables, fold in softened poha with turmeric and salt."
    }}
  ],
  "notes": "Hydrate with at least 2.5L water daily. Tailor portion sizes according to individual metabolic response."
}}
Only return valid JSON. Include all {days} days with {meals_per_day} meals per day.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text.strip())
        except Exception as e:
            logger.error(f"Gemini meal plan error: {e}")
            raise e

    async def chat(self, messages: List[Dict[str, str]], context: Optional[str] = None) -> str:
        prompt_parts = []
        if context:
            prompt_parts.append(f"System Context:\n{context}\n")
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role.capitalize()}: {content}")
            
        prompt_parts.append("Assistant:")
        full_prompt = "\n".join(prompt_parts)
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[full_prompt]
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            raise e

    async def transcribe_audio(self, audio_bytes: bytes, mime_type: str) -> str:
        prompt = "Transcribe this audio recording accurately. Return only the verbatim transcribed text without commentary."
        try:
            audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[audio_part, prompt]
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini audio transcription error: {e}")
            raise e
