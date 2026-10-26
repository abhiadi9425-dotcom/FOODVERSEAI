import base64
import json
import re
import io
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.services.ai.base import (
    BaseAIProvider,
    VisionFoodResult,
    FoodDetectionItem,
    FreshnessResult,
    HygieneAnalysisResult,
    FrameObservation,
)
from app.services.ai.rule_based_fallback import RuleBasedFallbackProvider

logger = logging.getLogger(__name__)


def clean_json_text(text: str) -> str:
    """Strips markdown code blocks and trims whitespace to extract raw JSON."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text


class GroqProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.vision_model = "qwen/qwen3.8-27b"
        self.chat_model = "qwen/qwen3.8-27b"
        self.whisper_model = "whisper-large-v3-turbo"
        self._fallback = RuleBasedFallbackProvider()

    async def analyze_food_image(self, image_bytes: bytes, mime_type: str) -> VisionFoodResult:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{b64}"
        prompt = """You are an expert food scientist and computer vision nutrition analyzer.
Examine this food image and identify the primary dish and up to 4 distinct visible ingredients.
Return a STRICT JSON object with this exact structure:
{
  "primary_food": "Accurate Name of Dish or Main Item",
  "confidence": 0.95,
  "detected_foods": [
    {
      "name": "Component or Ingredient Name",
      "confidence": 0.95,
      "alternate_names": ["alternate name"],
      "suggested_portion_g": 120,
      "reasoning": "Brief visual identification under 8 words"
    }
  ],
  "alternate_names": ["alternate name 1", "alternate name 2"],
  "estimated_portion_g": 350,
  "notes": "Brief serving or preparation observation."
}
Keep reasoning brief. Return valid JSON only."""
        try:
            resp = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_uri}}
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=700,
                temperature=0.2
            )
            raw = clean_json_text(resp.choices[0].message.content or "{}")
            data: Dict[str, Any] = {}
            try:
                data = json.loads(raw)
            except Exception as json_err:
                logger.warning(f"Groq JSON parse error ({json_err}), attempting regex extraction: {raw[:200]}")
                prim_match = re.search(r'"primary_food"\s*:\s*"([^"]+)"', raw)
                if prim_match:
                    data["primary_food"] = prim_match.group(1)
                portion_match = re.search(r'"estimated_portion_g"\s*:\s*([0-9.]+)', raw)
                if portion_match:
                    data["estimated_portion_g"] = float(portion_match.group(1))
                notes_match = re.search(r'"notes"\s*:\s*"([^"]+)"', raw)
                if notes_match:
                    data["notes"] = notes_match.group(1)
                names = re.findall(r'"name"\s*:\s*"([^"]+)"', raw)
                if names:
                    data["detected_foods"] = [{"name": n, "confidence": 0.9, "suggested_portion_g": 100} for n in names]

            primary_food = data.get("primary_food")
            if not primary_food and data.get("detected_foods"):
                primary_food = data["detected_foods"][0].get("name")
            if not primary_food:
                primary_food = "Recognized Food Item"

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
                primary_food=primary_food,
                confidence=data.get("confidence") or 0.92,
                alternate_names=data.get("alternate_names", []),
                estimated_portion_g=float(data.get("estimated_portion_g", 250)),
                notes=data.get("notes") or "Vision analysis completed via Groq Cloud vision.",
                provider_used=f"Groq Cloud ({self.vision_model})",
                is_live_ai=True
            )
        except Exception as e:
            logger.warning(f"Groq food vision error, utilizing safe fallback: {e}")
            return await self._fallback.analyze_food_image(image_bytes, mime_type)

    async def analyze_freshness(self, image_bytes: bytes, mime_type: str, category: str) -> FreshnessResult:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{b64}"
        prompt = f"""
You are a food freshness and visible spoilage assessment AI.
The user specifies this food category: "{category}".
Examine the visible exterior: discoloration, spots, mold mycelium, wilting, surface texture changes, bruising, or slime.
IMPORTANT SAFETY DIRECTIVE:
Visual appearance alone CANNOT establish that food is microbiologically safe. Pathogens can multiply without visible signs. Never guarantee that food is safe to consume.
Return STRICT JSON:
{{
  "assessment_category": "No obvious visual spoilage detected",
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
Choose assessment_category strictly from: "No obvious visual spoilage detected", "Visible quality concerns", or "Potential spoilage indicators".
Only return valid JSON. Do not wrap in markdown backticks.
"""
        try:
            resp = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_uri}}
                        ]
                    }
                ],
                max_tokens=600,
                temperature=0.2
            )
            raw = clean_json_text(resp.choices[0].message.content or "{}")
            data = json.loads(raw)
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
                provider_used=f"Groq Cloud ({self.vision_model})",
                is_live_ai=True
            )
        except Exception as e:
            logger.warning(f"Groq freshness error, utilizing safe protocol fallback: {e}")
            return await self._fallback.analyze_freshness(image_bytes, mime_type, category)

    async def analyze_hygiene_frames(self, frames: List[Dict[str, Any]]) -> HygieneAnalysisResult:
        user_content: List[Dict[str, Any]] = [
            {
                "type": "text",
                "text": """Inspect these sampled kitchen video frames. Evaluate visible indicators:
- Glove usage where raw or ready-to-eat foods are handled
- Hair restraints / hairnets / beard nets
- Cleanliness of food contact surfaces and cutting boards
- Visible cross-contamination risks
- Food separation and storage hygiene
IMPORTANT: Identify this as an AI-assisted preliminary observation, NOT an official health inspection certification.
Return STRICT JSON:
{
  "overall_summary": "Concise summary of overall visible hygiene practices across frames.",
  "overall_risk_level": "Low",
  "findings": [
    {
      "timestamp_s": 2.0,
      "category": "Glove Usage",
      "observation": "Food handler wearing clean food-grade gloves.",
      "severity": "Low",
      "confidence": 0.90
    }
  ],
  "practical_recommendations": [
    "Practical corrective recommendation 1"
  ],
  "disclaimer": "This is an AI-assisted visual overview from sampled video frames and does not constitute a legally binding health inspection."
}
Only return valid JSON."""
            }
        ]

        for f in frames[:4]:
            b64 = base64.b64encode(f["image_bytes"]).decode("utf-8")
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            })

        try:
            resp = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[{"role": "user", "content": user_content}],
                max_tokens=700,
                temperature=0.2
            )
            raw = clean_json_text(resp.choices[0].message.content or "{}")
            data = json.loads(raw)
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
                provider_used=f"Groq Cloud ({self.vision_model})",
                is_live_ai=True
            )
        except Exception as e:
            logger.warning(f"Groq hygiene error, utilizing baseline fallback: {e}")
            return await self._fallback.analyze_hygiene_frames(frames)

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
You are an expert chef. Create an authentic recipe.
User Request: {query}
Available Ingredients: {', '.join(ingredients) if ingredients else 'Standard pantry staples'}
Dietary Restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
Cuisine Preference: {cuisine}
Servings: {servings}
Cooking Time: {cooking_time or 30} minutes

Return STRICT JSON:
{{
  "title": "Recipe Title",
  "description": "Short appetizing description",
  "prep_time_min": 15,
  "cook_time_min": 20,
  "servings": {servings},
  "cuisine": "{cuisine}",
  "difficulty": "Easy",
  "ingredients": [
    {{"item": "Ingredient name", "quantity": "150g", "checked": false}}
  ],
  "instructions": [
    "Step 1: Description..."
  ],
  "substitutions": [
    {{"original": "Ingredient", "alternative": "Substitute", "reason": "Reason"}}
  ],
  "allergens": [],
  "estimated_nutrition": {{
    "calories_per_serving": 320,
    "protein_g": 8.5,
    "carbs_g": 48.0,
    "fat_g": 9.0,
    "fiber_g": 3.2
  }},
  "food_safety_notes": "Cook thoroughly to safe internal temperatures."
}}
Only return valid JSON without extra text.
"""
        try:
            resp = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            raw = clean_json_text(resp.choices[0].message.content or "{}")
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Groq recipe generation error, utilizing safe fallback: {e}")
            return await self._fallback.generate_recipe(
                query, ingredients, dietary_restrictions, cuisine, servings, cooking_time
            )

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
You are a precision clinical nutritionist.
Plan: {days} Days ({meals_per_day} meals per day).
Dietary Pattern: {dietary_pattern}
STRICT ALLERGIES (EXCLUDE ENTIRELY): {', '.join(allergies) if allergies else 'None'}
Restrictions: {', '.join(restrictions) if restrictions else 'None'}
Primary Goal: {goal}

CRITICAL: Keep output compact and concise so JSON is complete.
Return STRICT JSON:
{{
  "title": "{dietary_pattern.title()} Meal Plan ({goal.replace('_', ' ').title()})",
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
      "items": [{{"name": "Spinach", "quantity": "500g", "purchased": false}}]
    }}
  ],
  "meals": [
    {{
      "day_name": "Monday",
      "meal_type": "Breakfast",
      "recipe_name": "Dish Name",
      "serving_size": "1 serving",
      "calories": 350,
      "protein_g": 7.0,
      "carbs_g": 62.0,
      "fat_g": 8.0,
      "ingredients": ["Ingredient 1", "Ingredient 2"],
      "instructions": "Brief preparation instructions."
    }}
  ],
  "notes": "Hydrate adequately throughout the day."
}}
Include all {days} days with {meals_per_day} meals per day. Return valid JSON only.
"""
        try:
            resp = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.3
            )
            raw = clean_json_text(resp.choices[0].message.content or "{}")
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Groq meal plan generation error, utilizing safe fallback: {e}")
            return await self._fallback.generate_meal_plan(
                dietary_pattern, allergies, restrictions, goal, cuisine_preferences, meals_per_day, days
            )

    async def chat(self, messages: List[Dict[str, str]], context: Optional[str] = None) -> str:
        convo: List[Dict[str, str]] = []
        if context:
            convo.append({"role": "system", "content": context})
        convo.extend(messages)
        try:
            resp = self.client.chat.completions.create(
                model=self.chat_model,
                messages=convo,
                max_tokens=400,
                temperature=0.4
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            logger.error(f"Groq chat error: {e}")
            return await self._fallback.chat(messages, context)

    async def transcribe_audio(self, audio_bytes: bytes, mime_type: str) -> str:
        try:
            audio_file = io.BytesIO(audio_bytes)
            ext = ".mp3"
            if "webm" in mime_type:
                ext = ".webm"
            elif "wav" in mime_type:
                ext = ".wav"
            elif "m4a" in mime_type or "mp4" in mime_type:
                ext = ".m4a"
            audio_file.name = f"audio_input{ext}"

            transcription = self.client.audio.transcriptions.create(
                model=self.whisper_model,
                file=audio_file
            )
            return transcription.text.strip()
        except Exception as e:
            logger.error(f"Groq Whisper audio transcription error: {e}")
            return await self._fallback.transcribe_audio(audio_bytes, mime_type)
