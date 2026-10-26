import io
import pytest
from app.services.nutrition.calculator import NutritionCalculator
from app.services.nutrition.usda_data import VERIFIED_FOOD_DATABASE


def test_system_health(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "ai_providers" in data


def test_auth_workflow_and_isolation(client, auth_headers, secondary_auth_headers):
    # 1. Check me
    me_resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_resp.status_code == 200
    user_info = me_resp.json()
    assert user_info["user"]["email"] == "chef@foodverse.ai"

    # 2. Update profile
    prof_resp = client.put("/api/v1/profile", headers=auth_headers, json={
        "age": 30,
        "dietary_pattern": "vegetarian",
        "allergies": ["peanuts"],
        "goal": "muscle_gain",
        "cuisine_preferences": ["Indian", "Mediterranean"]
    })
    assert prof_resp.status_code == 200
    prof_data = prof_resp.json()
    assert prof_data["dietary_pattern"] == "vegetarian"
    assert "peanuts" in prof_data["allergies"]


def test_nutrition_calculation_pipeline():
    # Test verified scaling for Vegetable Poha (140 kcal per 100g, 250g serving = 350 kcal)
    result_100g = NutritionCalculator.calculate_scaled_nutrition("vegetable poha", serving_size_g=100.0)
    assert result_100g["calories"] == 140.0
    assert result_100g["protein_g"] == 2.8

    result_250g = NutritionCalculator.calculate_scaled_nutrition("vegetable poha", serving_size_g=250.0)
    assert result_250g["calories"] == 350.0
    assert result_250g["protein_g"] == 7.0
    assert result_250g["is_estimate"] is False
    assert "USDA" in result_250g["data_source"] or "ICMR" in result_250g["data_source"]


def test_food_analysis_and_user_isolation(client, auth_headers, secondary_auth_headers):
    # 1. User 1 analyzes and persists food
    resp = client.post("/api/v1/food/analyze", headers=auth_headers, data={
        "food_name": "Dal Tadka",
        "serving_size_g": "200"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["food_name"] == "Dal Tadka"
    assert data["calories"] == 236.0  # 118 * 2
    analysis_id = data["id"]
    assert analysis_id is not None

    # 2. User 1 gets history
    hist_resp = client.get("/api/v1/food/history", headers=auth_headers)
    assert hist_resp.status_code == 200
    items = hist_resp.json()
    assert any(item["id"] == analysis_id for item in items)

    # 3. User 2 must NOT have access to User 1's analysis
    user2_hist = client.get("/api/v1/food/history", headers=secondary_auth_headers)
    assert user2_hist.status_code == 200
    assert not any(item["id"] == analysis_id for item in user2_hist.json())

    # User 2 cannot fetch or delete User 1's record
    unauth_get = client.get(f"/api/v1/food/history/{analysis_id}", headers=secondary_auth_headers)
    assert unauth_get.status_code == 404

    unauth_del = client.delete(f"/api/v1/food/history/{analysis_id}", headers=secondary_auth_headers)
    assert unauth_del.status_code == 404

    # User 1 can delete
    del_resp = client.delete(f"/api/v1/food/history/{analysis_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    # 4. Test image upload food analysis
    from PIL import Image
    test_img = Image.new("RGB", (64, 64), color="orange")
    img_buf = io.BytesIO()
    test_img.save(img_buf, format="JPEG")
    img_buf.seek(0)
    upload_resp = client.post(
        "/api/v1/food/analyze",
        headers=auth_headers,
        files={"image": ("test_food.jpg", img_buf, "image/jpeg")},
        data={"serving_size_g": "150"}
    )
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    assert upload_data["food_name"] is not None
    assert upload_data["calories"] > 0


def test_freshness_assessment(client, auth_headers):
    from PIL import Image
    img = Image.new("RGB", (64, 64), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    resp = client.post(
        "/api/v1/freshness/analyze",
        headers=auth_headers,
        files={"image": ("test_apple.jpg", buf, "image/jpeg")},
        data={"food_category": "Fresh Produce / Fruits"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "assessment_category" in data
    assert "visual_observations" in data
    assert "safety_disclaimer" in data
    assert "microbiological" in data["safety_disclaimer"].lower() or "safety" in data["safety_disclaimer"].lower()


def test_cooking_assistant_and_recipe_saving(client, auth_headers):
    # 1. Generate recipe
    gen_resp = client.post("/api/v1/cooking/recipes", headers=auth_headers, json={
        "query": "High protein paneer bowl",
        "ingredients": ["Paneer", "Bell peppers", "Spices"],
        "dietary_restrictions": ["Vegetarian"],
        "cuisine": "Indian",
        "servings": 2,
        "cooking_time_min": 25
    })
    assert gen_resp.status_code == 200
    recipe_data = gen_resp.json()
    assert "title" in recipe_data
    assert "ingredients" in recipe_data

    # 2. Conversational refinement
    chat_resp = client.post("/api/v1/cooking/chat", headers=auth_headers, json={
        "message": "Can I substitute tofu for paneer to make it vegan?",
        "current_recipe": recipe_data
    })
    assert chat_resp.status_code == 200
    assert "reply" in chat_resp.json()

    # 3. Save recipe
    save_resp = client.post("/api/v1/cooking/save", headers=auth_headers, json={
        "title": recipe_data["title"],
        "description": recipe_data.get("description", "Delicious dish"),
        "prep_time_min": 15,
        "cook_time_min": 20,
        "servings": 2,
        "cuisine": "Indian",
        "difficulty": "Easy",
        "ingredients": recipe_data.get("ingredients", []),
        "instructions": recipe_data.get("instructions", []),
        "substitutions": recipe_data.get("substitutions", []),
        "allergens": ["dairy"],
        "estimated_nutrition": {"calories": 350, "protein_g": 20}
    })
    assert save_resp.status_code == 201
    saved = save_resp.json()
    assert saved["id"] is not None

    # List saved recipes
    list_resp = client.get("/api/v1/cooking/recipes", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


def test_meal_plan_generation_and_allergen_enforcement(client, auth_headers):
    # Generate 3-day meal plan with peanut allergy
    resp = client.post("/api/v1/meal-plans/generate", headers=auth_headers, json={
        "title": "Vegetarian Test Plan",
        "plan_type": "Daily",
        "days": 3,
        "meals_per_day": 3,
        "dietary_pattern": "vegetarian",
        "allergies": ["peanuts"],
        "goal": "maintenance"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["total_calories"] > 0
    assert len(data["meals"]) == 9  # 3 days * 3 meals

    # Verify no raw unhandled peanuts in meal names
    for m in data["meals"]:
        if "peanuts" in m["recipe_name"].lower():
            assert "substitute" in m["recipe_name"].lower() or "allergen-free" in m["recipe_name"].lower()

    # Toggle meal completion
    meal_id = data["meals"][0]["id"]
    status_resp = client.patch(f"/api/v1/meal-plans/meals/{meal_id}/status", headers=auth_headers, json={
        "is_completed": True
    })
    assert status_resp.status_code == 200
    assert status_resp.json()["is_completed"] is True


def test_multimodal_assistant_chat(client, auth_headers):
    resp = client.post("/api/v1/assistant/chat", headers=auth_headers, json={
        "message": "What are good breakfast options high in fiber?",
        "modality": "text"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert data["conversation_id"] is not None
