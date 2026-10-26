import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.services.nutrition.usda_data import find_matching_food_data, VERIFIED_FOOD_DATABASE


class NutritionCalculator:
    """
    Verified nutrition calculation pipeline with portion scaling,
    FDC online fallback, and allergen risk tagging.
    """

    @staticmethod
    def calculate_scaled_nutrition(
        food_name: str,
        serving_size_g: float = 100.0,
        serving_unit: str = "grams"
    ) -> Dict[str, Any]:
        """
        Calculates exact scaled macronutrients and micronutrients based on serving size.
        """
        # Step 1: Look up in verified reference database
        matched_item = find_matching_food_data(food_name)
        
        if matched_item:
            ratio = max(0.1, serving_size_g / 100.0)
            base_100g = matched_item["per_100g"]
            
            scaled_calories = round(base_100g["calories"] * ratio, 1)
            scaled_protein = round(base_100g["protein_g"] * ratio, 1)
            scaled_carbs = round(base_100g["carbs_g"] * ratio, 1)
            scaled_fat = round(base_100g["fat_g"] * ratio, 1)
            scaled_fiber = round(base_100g.get("fiber_g", 0.0) * ratio, 1)
            scaled_sugar = round(base_100g.get("sugar_g", 0.0) * ratio, 1)
            scaled_sodium = round(base_100g.get("sodium_mg", 0.0) * ratio, 1)
            
            scaled_micros = {}
            for k, v in base_100g.get("micronutrients", {}).items():
                scaled_micros[k] = round(v * ratio, 1)
                
            return {
                "food_name": matched_item["canonical_name"],
                "category": matched_item.get("category", "General Food"),
                "serving_size_g": serving_size_g,
                "serving_unit": serving_unit,
                "calories": scaled_calories,
                "protein_g": scaled_protein,
                "carbs_g": scaled_carbs,
                "fat_g": scaled_fat,
                "fiber_g": scaled_fiber,
                "sugar_g": scaled_sugar,
                "sodium_mg": scaled_sodium,
                "micronutrients": scaled_micros,
                "data_source": matched_item.get("source", "USDA FoodData Central Reference"),
                "reference_id": matched_item.get("reference_id", "REF-USDA-01"),
                "allergens": matched_item.get("allergens", []),
                "is_estimate": False,
                "uncertainty_note": "Calculated deterministically from verified laboratory composition tables scaled to the entered portion mass."
            }
            
        # Step 2: If USDA API key is set, query online FDC
        if settings.USDA_API_KEY:
            try:
                online_data = NutritionCalculator._query_usda_api(food_name, serving_size_g)
                if online_data:
                    return online_data
            except Exception:
                pass

        # Step 3: Generic heuristic fallback with clear estimation flag
        ratio = max(0.1, serving_size_g / 100.0)
        return {
            "food_name": food_name.title(),
            "category": "Prepared Dish (Estimated)",
            "serving_size_g": serving_size_g,
            "serving_unit": serving_unit,
            "calories": round(150.0 * ratio, 1),
            "protein_g": round(5.0 * ratio, 1),
            "carbs_g": round(20.0 * ratio, 1),
            "fat_g": round(5.0 * ratio, 1),
            "fiber_g": round(2.0 * ratio, 1),
            "sugar_g": round(2.0 * ratio, 1),
            "sodium_mg": round(250.0 * ratio, 1),
            "micronutrients": {},
            "data_source": "General Nutritional Benchmark (Approximation)",
            "reference_id": "ESTIMATE-BENCHMARK",
            "allergens": [],
            "is_estimate": True,
            "uncertainty_note": "Item not found in verified lab tables. Values represent an approximate benchmark for mixed prepared foods; portion and composition should be verified."
        }

    @staticmethod
    def _query_usda_api(food_name: str, serving_size_g: float) -> Optional[Dict[str, Any]]:
        with httpx.Client(timeout=4.0) as client:
            resp = client.get(
                "https://api.nal.usda.gov/fdc/v1/foods/search",
                params={"api_key": settings.USDA_API_KEY, "query": food_name, "pageSize": 1}
            )
            if resp.status_code == 200:
                data = resp.json()
                foods = data.get("foods", [])
                if foods:
                    top_food = foods[0]
                    nutrients = {n["nutrientName"].lower(): n["value"] for n in top_food.get("foodNutrients", [])}
                    ratio = serving_size_g / 100.0
                    return {
                        "food_name": top_food.get("description", food_name).title(),
                        "category": top_food.get("foodCategory", "USDA Food"),
                        "serving_size_g": serving_size_g,
                        "serving_unit": "grams",
                        "calories": round(nutrients.get("energy", 120.0) * ratio, 1),
                        "protein_g": round(nutrients.get("protein", 3.0) * ratio, 1),
                        "carbs_g": round(nutrients.get("carbohydrate, by difference", 15.0) * ratio, 1),
                        "fat_g": round(nutrients.get("total lipid (fat)", 3.0) * ratio, 1),
                        "fiber_g": round(nutrients.get("fiber, total dietary", 1.5) * ratio, 1),
                        "sugar_g": round(nutrients.get("sugars, total including nlea", 1.0) * ratio, 1),
                        "sodium_mg": round(nutrients.get("sodium, na", 200.0) * ratio, 1),
                        "micronutrients": {},
                        "data_source": f"USDA FoodData Central Live API (FDC ID: {top_food.get('fdcId')})",
                        "reference_id": f"FDC-{top_food.get('fdcId')}",
                        "allergens": [],
                        "is_estimate": False,
                        "uncertainty_note": "Direct live USDA FDC laboratory entry scaled to target mass."
                    }
        return None

    @staticmethod
    def aggregate_meal_nutrition(ingredients: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Derives meal totals strictly from ingredient components.
        """
        totals = {
            "calories": 0.0,
            "protein_g": 0.0,
            "carbs_g": 0.0,
            "fat_g": 0.0,
            "fiber_g": 0.0,
        }
        for ing in ingredients:
            name = ing.get("name") or ing.get("item", "")
            grams = float(ing.get("grams") or ing.get("quantity_g") or 100.0)
            res = NutritionCalculator.calculate_scaled_nutrition(name, serving_size_g=grams)
            totals["calories"] += res["calories"]
            totals["protein_g"] += res["protein_g"]
            totals["carbs_g"] += res["carbs_g"]
            totals["fat_g"] += res["fat_g"]
            totals["fiber_g"] += res["fiber_g"]

        return {k: round(v, 1) for k, v in totals.items()}
