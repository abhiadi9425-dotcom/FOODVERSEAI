import base64
import json
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

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.model_name = "gpt-4o"

    async def analyze_food_image(self, image_bytes: bytes, mime_type: str) -> VisionFoodResult:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{b64}"
        system_prompt = "You are a professional food recognition AI. Output strictly valid JSON."
        user_prompt = """Analyze this food image. Return STRICT JSON:
{
  "detected_foods": [
    {"name": "Food Name", "confidence": 0.95, "alternate_names": ["synonym"], "suggested_portion_g": 200, "reasoning": "Visual characteristics"}
  ],
  "primary_food": "Primary dish name",
  "confidence": 0.92,
  "alternate_names": ["synonym"],
  "estimated_portion_g": 200,
  "notes": "Estimated portion."
}"""
        try:
            resp = self.client.chat.completions.create(
                model=self.model_name,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": data_uri}}
                    ]}
                ]
            )
            data = json.loads(resp.choices[0].message.content)
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
                provider_used=f"OpenAI ({self.model_name})",
                is_live_ai=True
            )
        except Exception as e:
            logger.error(f"OpenAI food vision error: {e}")
            raise e

    async def analyze_freshness(self, image_bytes: bytes, mime_type: str, category: str) -> FreshnessResult:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{b64}"
        prompt = f"""Examine this food item (Category: {category}) for visible signs of decay or spoilage.
IMPORTANT: Visual appearance alone cannot determine microbiological safety.
Return STRICT JSON:
{{
  "assessment_category": "No obvious visual spoilage detected" OR "Visible quality concerns" OR "Potential spoilage indicators",
  "confidence": 0.90,
  "visual_observations": ["detail 1", "detail 2"],
  "recommendations": ["recommendation 1"],
  "safety_disclaimer": "Visual assessment cannot guarantee microbiological safety."
}}"""
        try:
            resp = self.client.chat.completions.create(
                model=self.model_name,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_uri}}
                    ]}
                ]
            )
            data = json.loads(resp.choices[0].message.content)
            return FreshnessResult(
                food_category=category,
                assessment_category=data.get("assessment_category", "Visible quality concerns"),
                confidence=data.get("confidence"),
                visual_observations=data.get("visual_observations", []),
                recommendations=data.get("recommendations", []),
                safety_disclaimer=data.get("safety_disclaimer", "Visual assessment cannot guarantee microbiological safety."),
                provider_used=f"OpenAI ({self.model_name})",
                is_live_ai=True
            )
        except Exception as e:
            logger.error(f"OpenAI freshness error: {e}")
            raise e

    async def analyze_hygiene_frames(self, frames: List[Dict[str, Any]]) -> HygieneAnalysisResult:
        user_content = [{"type": "text", "text": "Analyze these kitchen video frames for hygiene indicators. Return strict JSON with overall_summary, overall_risk_level, findings, practical_recommendations, disclaimer."}]
        for f in frames[:5]:
            b64 = base64.b64encode(f["image_bytes"]).decode("utf-8")
            user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
        try:
            resp = self.client.chat.completions.create(
                model=self.model_name,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": user_content}]
            )
            data = json.loads(resp.choices[0].message.content)
            findings = [
                FrameObservation(
                    timestamp_s=float(item.get("timestamp_s", 0.0)),
                    category=item.get("category", "Cleanliness"),
                    observation=item.get("observation", ""),
                    severity=item.get("severity", "Low"),
                    confidence=item.get("confidence")
                )
                for item in data.get("findings", [])
            ]
            return HygieneAnalysisResult(
                overall_summary=data.get("overall_summary", "Observations complete."),
                overall_risk_level=data.get("overall_risk_level", "Moderate"),
                findings=findings,
                practical_recommendations=data.get("practical_recommendations", []),
                disclaimer=data.get("disclaimer", "Preliminary AI observations only."),
                provider_used=f"OpenAI ({self.model_name})",
                is_live_ai=True
            )
        except Exception as e:
            logger.error(f"OpenAI hygiene error: {e}")
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
        prompt = f"Create a recipe for '{query}' with ingredients {ingredients}, restrictions {dietary_restrictions}, cuisine {cuisine}, servings {servings}. Return valid JSON."
        resp = self.client.chat.completions.create(
            model=self.model_name,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(resp.choices[0].message.content)

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
        prompt = f"Create a {days}-day meal plan for {dietary_pattern}, strict allergies: {allergies}, goal: {goal}. Return JSON with title, grocery_list, meals."
        resp = self.client.chat.completions.create(
            model=self.model_name,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(resp.choices[0].message.content)

    async def chat(self, messages: List[Dict[str, str]], context: Optional[str] = None) -> str:
        convo = []
        if context:
            convo.append({"role": "system", "content": context})
        convo.extend(messages)
        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=convo
        )
        return resp.choices[0].message.content.strip()

    async def transcribe_audio(self, audio_bytes: bytes, mime_type: str) -> str:
        import io
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "recording.mp3"
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcription.text.strip()
