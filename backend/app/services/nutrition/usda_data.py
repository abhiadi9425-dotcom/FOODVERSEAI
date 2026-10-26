"""
USDA FoodData Central and verified reference nutrition dataset.
Nutritional values are standardized per 100 grams.
Sources: USDA FoodData Central (FDC) & Indian Council of Medical Research (ICMR) reference tables.
"""

from typing import Dict, Any, Optional

VERIFIED_FOOD_DATABASE: Dict[str, Dict[str, Any]] = {
    "vegetable poha": {
        "canonical_name": "Vegetable Poha",
        "category": "Indian Breakfast / Grain",
        "default_serving_g": 250,
        "serving_description": "1 medium bowl (approx. 250g)",
        "per_100g": {
            "calories": 140.0,
            "protein_g": 2.8,
            "carbs_g": 25.4,
            "fat_g": 3.2,
            "fiber_g": 2.1,
            "sugar_g": 1.4,
            "sodium_mg": 280.0,
            "micronutrients": {"iron_mg": 3.8, "vitamin_c_mg": 8.5, "calcium_mg": 22.0, "potassium_mg": 140.0}
        },
        "allergens": ["mustard", "peanuts"],
        "source": "USDA / ICMR Food Composition Tables",
        "reference_id": "ICMR-IN-041",
        "synonyms": ["poha", "flattened rice", "kanda poha", "batata poha", "chivda"]
    },
    "dal tadka": {
        "canonical_name": "Dal Tadka",
        "category": "Legumes & Pulses",
        "default_serving_g": 200,
        "serving_description": "1 cup / katori (approx. 200g)",
        "per_100g": {
            "calories": 118.0,
            "protein_g": 6.8,
            "carbs_g": 15.2,
            "fat_g": 3.6,
            "fiber_g": 4.5,
            "sugar_g": 1.1,
            "sodium_mg": 310.0,
            "micronutrients": {"iron_mg": 2.4, "potassium_mg": 290.0, "calcium_mg": 35.0}
        },
        "allergens": [],
        "source": "USDA FoodData Central / FDC ID: 172429",
        "reference_id": "FDC-172429",
        "synonyms": ["yellow dal", "toor dal", "lentil soup", "tadka dal", "daal"]
    },
    "paneer tikka": {
        "canonical_name": "Paneer Tikka",
        "category": "Dairy / Appetizer",
        "default_serving_g": 180,
        "serving_description": "5-6 pieces with grilled bell peppers (approx. 180g)",
        "per_100g": {
            "calories": 245.0,
            "protein_g": 14.5,
            "carbs_g": 6.2,
            "fat_g": 18.0,
            "fiber_g": 1.8,
            "sugar_g": 2.5,
            "sodium_mg": 360.0,
            "micronutrients": {"calcium_mg": 380.0, "vitamin_a_iu": 420.0, "iron_mg": 1.2}
        },
        "allergens": ["dairy"],
        "source": "USDA FoodData Central / ICMR Dairy Tables",
        "reference_id": "FDC-171249",
        "synonyms": ["tandoori paneer", "grilled paneer", "cottage cheese tikka"]
    },
    "chana masala": {
        "canonical_name": "Chana Masala",
        "category": "Legumes & Curries",
        "default_serving_g": 220,
        "serving_description": "1 medium bowl (approx. 220g)",
        "per_100g": {
            "calories": 135.0,
            "protein_g": 6.2,
            "carbs_g": 19.8,
            "fat_g": 3.8,
            "fiber_g": 5.2,
            "sugar_g": 2.1,
            "sodium_mg": 380.0,
            "micronutrients": {"iron_mg": 2.6, "potassium_mg": 280.0, "folate_mcg": 52.0}
        },
        "allergens": [],
        "source": "USDA FoodData Central / FDC ID: 173757",
        "reference_id": "FDC-173757",
        "synonyms": ["chole", "chickpea curry", "kabuli chana curry"]
    },
    "palak paneer": {
        "canonical_name": "Palak Paneer",
        "category": "Vegetable & Dairy Curry",
        "default_serving_g": 220,
        "serving_description": "1 medium bowl (approx. 220g)",
        "per_100g": {
            "calories": 165.0,
            "protein_g": 8.5,
            "carbs_g": 5.4,
            "fat_g": 12.5,
            "fiber_g": 3.1,
            "sugar_g": 1.8,
            "sodium_mg": 320.0,
            "micronutrients": {"iron_mg": 3.2, "calcium_mg": 280.0, "vitamin_a_iu": 1850.0}
        },
        "allergens": ["dairy"],
        "source": "USDA / ICMR Food Tables",
        "reference_id": "ICMR-VEG-082",
        "synonyms": ["spinach paneer", "saag paneer"]
    },
    "vegetable biryani": {
        "canonical_name": "Vegetable Biryani",
        "category": "Rice Specialties",
        "default_serving_g": 300,
        "serving_description": "1 generous plate (approx. 300g)",
        "per_100g": {
            "calories": 162.0,
            "protein_g": 3.8,
            "carbs_g": 27.5,
            "fat_g": 4.2,
            "fiber_g": 2.6,
            "sugar_g": 1.5,
            "sodium_mg": 340.0,
            "micronutrients": {"iron_mg": 1.4, "potassium_mg": 160.0}
        },
        "allergens": ["dairy"],
        "source": "USDA / Verified Reference Database",
        "reference_id": "FDC-210492",
        "synonyms": ["veg biryani", "vegetable pulao", "pulao"]
    },
    "roti / chapati": {
        "canonical_name": "Whole Wheat Roti / Chapati",
        "category": "Flatbreads",
        "default_serving_g": 40,
        "serving_description": "1 medium 6-inch roti (approx. 40g)",
        "per_100g": {
            "calories": 264.0,
            "protein_g": 9.2,
            "carbs_g": 52.0,
            "fat_g": 2.5,
            "fiber_g": 7.8,
            "sugar_g": 1.2,
            "sodium_mg": 180.0,
            "micronutrients": {"iron_mg": 3.1, "magnesium_mg": 74.0}
        },
        "allergens": ["gluten", "wheat"],
        "source": "USDA FoodData Central / FDC ID: 172778",
        "reference_id": "FDC-172778",
        "synonyms": ["roti", "chapati", "phulka", "whole wheat flatbread"]
    },
    "idli with sambar": {
        "canonical_name": "Steamed Idli with Sambar",
        "category": "South Indian Breakfast",
        "default_serving_g": 240,
        "serving_description": "2 idlis (100g) with 1 cup sambar (140g)",
        "per_100g": {
            "calories": 112.0,
            "protein_g": 4.1,
            "carbs_g": 21.6,
            "fat_g": 1.1,
            "fiber_g": 2.8,
            "sugar_g": 1.9,
            "sodium_mg": 290.0,
            "micronutrients": {"iron_mg": 1.8, "potassium_mg": 195.0}
        },
        "allergens": ["mustard"],
        "source": "USDA / ICMR Tables",
        "reference_id": "ICMR-SI-012",
        "synonyms": ["idli", "idli sambar", "steamed rice cake"]
    },
    "masala dosa": {
        "canonical_name": "Masala Dosa",
        "category": "South Indian Specialties",
        "default_serving_g": 200,
        "serving_description": "1 medium stuffed dosa (approx. 200g)",
        "per_100g": {
            "calories": 195.0,
            "protein_g": 4.8,
            "carbs_g": 29.5,
            "fat_g": 6.8,
            "fiber_g": 2.4,
            "sugar_g": 1.2,
            "sodium_mg": 340.0,
            "micronutrients": {"iron_mg": 1.9, "potassium_mg": 180.0}
        },
        "allergens": ["mustard"],
        "source": "USDA / ICMR Reference",
        "reference_id": "ICMR-SI-028",
        "synonyms": ["dosa", "potato dosa", "crispy crepe"]
    },
    "grilled chicken breast": {
        "canonical_name": "Grilled Chicken Breast",
        "category": "Poultry / Lean Protein",
        "default_serving_g": 150,
        "serving_description": "1 breast fillet (approx. 150g)",
        "per_100g": {
            "calories": 165.0,
            "protein_g": 31.0,
            "carbs_g": 0.0,
            "fat_g": 3.6,
            "fiber_g": 0.0,
            "sugar_g": 0.0,
            "sodium_mg": 74.0,
            "micronutrients": {"iron_mg": 1.0, "potassium_mg": 256.0, "phosphorus_mg": 228.0}
        },
        "allergens": [],
        "source": "USDA FoodData Central / FDC ID: 171077",
        "reference_id": "FDC-171077",
        "synonyms": ["chicken breast", "grilled chicken", "roast chicken breast"]
    },
    "baked salmon": {
        "canonical_name": "Baked Wild Atlantic Salmon",
        "category": "Fish / Seafood",
        "default_serving_g": 150,
        "serving_description": "1 fillet (approx. 150g)",
        "per_100g": {
            "calories": 206.0,
            "protein_g": 22.1,
            "carbs_g": 0.0,
            "fat_g": 12.3,
            "fiber_g": 0.0,
            "sugar_g": 0.0,
            "sodium_mg": 61.0,
            "micronutrients": {"omega_3_g": 2.2, "vitamin_d_iu": 570.0, "potassium_mg": 490.0}
        },
        "allergens": ["fish"],
        "source": "USDA FoodData Central / FDC ID: 173686",
        "reference_id": "FDC-173686",
        "synonyms": ["salmon", "grilled salmon", "salmon fillet"]
    },
    "avocado toast": {
        "canonical_name": "Avocado Toast on Whole Grain",
        "category": "Breakfast / Toast",
        "default_serving_g": 160,
        "serving_description": "1 large slice (approx. 160g)",
        "per_100g": {
            "calories": 198.0,
            "protein_g": 5.4,
            "carbs_g": 18.2,
            "fat_g": 12.0,
            "fiber_g": 6.8,
            "sugar_g": 1.8,
            "sodium_mg": 240.0,
            "micronutrients": {"potassium_mg": 380.0, "folate_mcg": 72.0, "vitamin_e_mg": 2.1}
        },
        "allergens": ["gluten", "wheat"],
        "source": "USDA FoodData Central / Verified Composition",
        "reference_id": "FDC-219481",
        "synonyms": ["avocado on toast", "guacamole toast"]
    },
    "greek salad": {
        "canonical_name": "Mediterranean Greek Salad",
        "category": "Salads",
        "default_serving_g": 200,
        "serving_description": "1 medium bowl with feta & olives (approx. 200g)",
        "per_100g": {
            "calories": 95.0,
            "protein_g": 3.2,
            "carbs_g": 4.8,
            "fat_g": 7.2,
            "fiber_g": 1.6,
            "sugar_g": 2.9,
            "sodium_mg": 340.0,
            "micronutrients": {"calcium_mg": 85.0, "vitamin_c_mg": 14.0}
        },
        "allergens": ["dairy"],
        "source": "USDA FoodData Central / FDC ID: 170420",
        "reference_id": "FDC-170420",
        "synonyms": ["feta salad", "mediterranean salad", "cucumber tomato salad"]
    },
    "boiled egg": {
        "canonical_name": "Hard Boiled Egg",
        "category": "Eggs / Protein",
        "default_serving_g": 50,
        "serving_description": "1 large egg (approx. 50g)",
        "per_100g": {
            "calories": 155.0,
            "protein_g": 12.6,
            "carbs_g": 1.1,
            "fat_g": 10.6,
            "fiber_g": 0.0,
            "sugar_g": 1.1,
            "sodium_mg": 124.0,
            "micronutrients": {"choline_mg": 294.0, "vitamin_b12_mcg": 1.1, "iron_mg": 1.2}
        },
        "allergens": ["eggs"],
        "source": "USDA FoodData Central / FDC ID: 171287",
        "reference_id": "FDC-171287",
        "synonyms": ["egg", "boiled eggs", "hard boiled eggs"]
    },
    "steamed brown rice": {
        "canonical_name": "Steamed Brown Rice",
        "category": "Grains",
        "default_serving_g": 150,
        "serving_description": "1 cup cooked (approx. 150g)",
        "per_100g": {
            "calories": 111.0,
            "protein_g": 2.6,
            "carbs_g": 23.0,
            "fat_g": 0.9,
            "fiber_g": 1.8,
            "sugar_g": 0.4,
            "sodium_mg": 5.0,
            "micronutrients": {"magnesium_mg": 43.0, "phosphorus_mg": 83.0}
        },
        "allergens": [],
        "source": "USDA FoodData Central / FDC ID: 169704",
        "reference_id": "FDC-169704",
        "synonyms": ["brown rice", "cooked brown rice"]
    },
    "steamed broccoli": {
        "canonical_name": "Steamed Fresh Broccoli",
        "category": "Cruciferous Vegetables",
        "default_serving_g": 100,
        "serving_description": "1 cup florets (approx. 100g)",
        "per_100g": {
            "calories": 35.0,
            "protein_g": 2.4,
            "carbs_g": 7.2,
            "fat_g": 0.4,
            "fiber_g": 3.3,
            "sugar_g": 1.4,
            "sodium_mg": 41.0,
            "micronutrients": {"vitamin_c_mg": 64.9, "vitamin_k_mcg": 141.0, "calcium_mg": 40.0}
        },
        "allergens": [],
        "source": "USDA FoodData Central / FDC ID: 170379",
        "reference_id": "FDC-170379",
        "synonyms": ["broccoli", "cooked broccoli"]
    },
    "fresh apple": {
        "canonical_name": "Fresh Apple with Skin",
        "category": "Fresh Fruits",
        "default_serving_g": 182,
        "serving_description": "1 medium apple (approx. 182g)",
        "per_100g": {
            "calories": 52.0,
            "protein_g": 0.3,
            "carbs_g": 13.8,
            "fat_g": 0.2,
            "fiber_g": 2.4,
            "sugar_g": 10.4,
            "sodium_mg": 1.0,
            "micronutrients": {"potassium_mg": 107.0, "vitamin_c_mg": 4.6}
        },
        "allergens": [],
        "source": "USDA FoodData Central / FDC ID: 171688",
        "reference_id": "FDC-171688",
        "synonyms": ["apple", "red apple", "green apple", "crisp apple"]
    },
    "fresh banana": {
        "canonical_name": "Fresh Ripe Banana",
        "category": "Fresh Fruits",
        "default_serving_g": 118,
        "serving_description": "1 medium banana (approx. 118g)",
        "per_100g": {
            "calories": 89.0,
            "protein_g": 1.1,
            "carbs_g": 22.8,
            "fat_g": 0.3,
            "fiber_g": 2.6,
            "sugar_g": 12.2,
            "sodium_mg": 1.0,
            "micronutrients": {"potassium_mg": 358.0, "vitamin_b6_mg": 0.4}
        },
        "allergens": [],
        "source": "USDA FoodData Central / FDC ID: 173944",
        "reference_id": "FDC-173944",
        "synonyms": ["banana", "yellow banana", "ripe banana"]
    },
    "plain greek yogurt": {
        "canonical_name": "Plain Low-Fat Greek Yogurt",
        "category": "Dairy",
        "default_serving_g": 170,
        "serving_description": "1 cup container (approx. 170g)",
        "per_100g": {
            "calories": 73.0,
            "protein_g": 10.0,
            "carbs_g": 3.9,
            "fat_g": 2.0,
            "fiber_g": 0.0,
            "sugar_g": 3.6,
            "sodium_mg": 36.0,
            "micronutrients": {"calcium_mg": 115.0, "potassium_mg": 141.0}
        },
        "allergens": ["dairy"],
        "source": "USDA FoodData Central / FDC ID: 171284",
        "reference_id": "FDC-171284",
        "synonyms": ["greek yogurt", "curd", "dahi", "plain yogurt"]
    },
    "hummus with pita": {
        "canonical_name": "Traditional Chickpea Hummus",
        "category": "Dips & Spreads",
        "default_serving_g": 60,
        "serving_description": "4 tbsp (approx. 60g)",
        "per_100g": {
            "calories": 166.0,
            "protein_g": 7.9,
            "carbs_g": 14.3,
            "fat_g": 9.6,
            "fiber_g": 6.0,
            "sugar_g": 0.6,
            "sodium_mg": 379.0,
            "micronutrients": {"iron_mg": 2.4, "folate_mcg": 83.0}
        },
        "allergens": ["sesame"],
        "source": "USDA FoodData Central / FDC ID: 173799",
        "reference_id": "FDC-173799",
        "synonyms": ["hummus", "chickpea dip", "tahini hummus"]
    },
    "chicken quinoa bowl": {
        "canonical_name": "Chicken & Quinoa Grain Bowl",
        "category": "Grain Bowls / Balanced Meals",
        "default_serving_g": 350,
        "serving_description": "1 wholesome grain bowl (approx. 350g)",
        "per_100g": {
            "calories": 155.0,
            "protein_g": 12.8,
            "carbs_g": 14.5,
            "fat_g": 4.8,
            "fiber_g": 2.6,
            "sugar_g": 1.5,
            "sodium_mg": 240.0,
            "micronutrients": {"iron_mg": 1.8, "potassium_mg": 320.0, "calcium_mg": 45.0}
        },
        "allergens": [],
        "source": "USDA FoodData Central / FDC ID: 168917",
        "reference_id": "FDC-168917",
        "synonyms": ["quinoa bowl", "chicken bowl", "mediterranean bowl", "grain bowl", "protein bowl", "chicken and quinoa"]
    },
    "cheese pizza": {
        "canonical_name": "Cheese Pizza",
        "category": "Prepared Entrees",
        "default_serving_g": 107,
        "serving_description": "1 regular slice (approx. 107g)",
        "per_100g": {
            "calories": 266.0,
            "protein_g": 11.4,
            "carbs_g": 33.3,
            "fat_g": 9.8,
            "fiber_g": 2.3,
            "sugar_g": 3.6,
            "sodium_mg": 598.0,
            "micronutrients": {"calcium_mg": 188.0, "iron_mg": 2.5, "potassium_mg": 172.0}
        },
        "allergens": ["dairy", "gluten"],
        "source": "USDA FoodData Central / FDC ID: 170940",
        "reference_id": "FDC-170940",
        "synonyms": ["pizza", "margherita", "slice of pizza", "pepperoni pizza", "flatbread pizza"]
    },
    "cheeseburger": {
        "canonical_name": "Cheeseburger with Bun",
        "category": "Sandwiches & Burgers",
        "default_serving_g": 160,
        "serving_description": "1 single patty burger with bun (approx. 160g)",
        "per_100g": {
            "calories": 257.0,
            "protein_g": 13.5,
            "carbs_g": 24.2,
            "fat_g": 12.1,
            "fiber_g": 1.4,
            "sugar_g": 4.2,
            "sodium_mg": 490.0,
            "micronutrients": {"iron_mg": 2.8, "calcium_mg": 120.0, "potassium_mg": 210.0}
        },
        "allergens": ["dairy", "gluten"],
        "source": "USDA FoodData Central / FDC ID: 171120",
        "reference_id": "FDC-171120",
        "synonyms": ["burger", "hamburger", "veggie burger", "beef burger", "patty"]
    },
    "pasta marinara": {
        "canonical_name": "Pasta with Tomato Marinara",
        "category": "Pasta & Grains",
        "default_serving_g": 250,
        "serving_description": "1 cup cooked pasta with sauce (approx. 250g)",
        "per_100g": {
            "calories": 131.0,
            "protein_g": 4.5,
            "carbs_g": 24.8,
            "fat_g": 1.6,
            "fiber_g": 2.1,
            "sugar_g": 3.2,
            "sodium_mg": 310.0,
            "micronutrients": {"iron_mg": 1.2, "potassium_mg": 230.0, "vitamin_c_mg": 5.4}
        },
        "allergens": ["gluten"],
        "source": "USDA FoodData Central / FDC ID: 168927",
        "reference_id": "FDC-168927",
        "synonyms": ["pasta", "spaghetti", "penne", "macaroni", "noodles", "pasta with sauce"]
    },
    "garden salad": {
        "canonical_name": "Fresh Garden Salad with Vegetables",
        "category": "Salads",
        "default_serving_g": 150,
        "serving_description": "1 large bowl mixed greens (approx. 150g)",
        "per_100g": {
            "calories": 42.0,
            "protein_g": 1.6,
            "carbs_g": 4.8,
            "fat_g": 1.8,
            "fiber_g": 2.2,
            "sugar_g": 2.1,
            "sodium_mg": 120.0,
            "micronutrients": {"vitamin_a_iu": 1800.0, "vitamin_c_mg": 18.0, "iron_mg": 1.1}
        },
        "allergens": [],
        "source": "USDA FoodData Central / FDC ID: 168882",
        "reference_id": "FDC-168882",
        "synonyms": ["salad", "green salad", "mixed salad", "caesar salad", "lettuce salad", "vegetable salad"]
    },
    "oatmeal with fruit": {
        "canonical_name": "Cooked Rolled Oatmeal",
        "category": "Breakfast Grains",
        "default_serving_g": 240,
        "serving_description": "1 medium bowl (approx. 240g)",
        "per_100g": {
            "calories": 71.0,
            "protein_g": 2.5,
            "carbs_g": 12.0,
            "fat_g": 1.4,
            "fiber_g": 1.7,
            "sugar_g": 0.8,
            "sodium_mg": 49.0,
            "micronutrients": {"iron_mg": 0.9, "magnesium_mg": 27.0, "phosphorus_mg": 77.0}
        },
        "allergens": [],
        "source": "USDA FoodData Central / FDC ID: 170688",
        "reference_id": "FDC-170688",
        "synonyms": ["oatmeal", "oats", "porridge", "rolled oats"]
    },
    "vegetable omelette": {
        "canonical_name": "Vegetable Egg Omelette",
        "category": "Eggs / Breakfast",
        "default_serving_g": 150,
        "serving_description": "2-egg omelette with herbs and bell peppers (approx. 150g)",
        "per_100g": {
            "calories": 154.0,
            "protein_g": 10.6,
            "carbs_g": 2.4,
            "fat_g": 11.2,
            "fiber_g": 0.6,
            "sugar_g": 1.2,
            "sodium_mg": 310.0,
            "micronutrients": {"choline_mg": 180.0, "vitamin_a_iu": 540.0, "iron_mg": 1.6}
        },
        "allergens": ["egg"],
        "source": "USDA FoodData Central / FDC ID: 172186",
        "reference_id": "FDC-172186",
        "synonyms": ["omelette", "omelet", "scrambled eggs", "fried egg", "egg bhurji"]
    },
    "burrito bowl": {
        "canonical_name": "Mexican Bean & Rice Burrito Bowl",
        "category": "Bowls / Entrees",
        "default_serving_g": 350,
        "serving_description": "1 loaded burrito bowl with beans and salsa (approx. 350g)",
        "per_100g": {
            "calories": 142.0,
            "protein_g": 5.8,
            "carbs_g": 22.4,
            "fat_g": 3.6,
            "fiber_g": 4.2,
            "sugar_g": 1.8,
            "sodium_mg": 380.0,
            "micronutrients": {"iron_mg": 1.9, "potassium_mg": 280.0, "folate_mcg": 52.0}
        },
        "allergens": [],
        "source": "USDA FoodData Central / FDC ID: 170725",
        "reference_id": "FDC-170725",
        "synonyms": ["burrito", "burrito bowl", "taco bowl", "fajita bowl", "mexican bowl"]
    },
    "tofu stir fry": {
        "canonical_name": "Tofu & Vegetable Stir Fry",
        "category": "Vegetarian Entrees",
        "default_serving_g": 250,
        "serving_description": "1 plate tofu with stir-fried greens (approx. 250g)",
        "per_100g": {
            "calories": 98.0,
            "protein_g": 7.8,
            "carbs_g": 5.4,
            "fat_g": 5.6,
            "fiber_g": 2.4,
            "sugar_g": 1.9,
            "sodium_mg": 320.0,
            "micronutrients": {"calcium_mg": 160.0, "iron_mg": 2.2, "potassium_mg": 220.0}
        },
        "allergens": ["soy"],
        "source": "USDA FoodData Central / FDC ID: 172448",
        "reference_id": "FDC-172448",
        "synonyms": ["tofu", "tofu stir-fry", "stir fry", "tofu bowl", "bean curd"]
    },
    "chicken curry": {
        "canonical_name": "Chicken Curry / Tikka Masala",
        "category": "Poultry / Curries",
        "default_serving_g": 220,
        "serving_description": "1 cup boneless chicken curry (approx. 220g)",
        "per_100g": {
            "calories": 150.0,
            "protein_g": 14.8,
            "carbs_g": 4.5,
            "fat_g": 8.2,
            "fiber_g": 1.2,
            "sugar_g": 2.0,
            "sodium_mg": 380.0,
            "micronutrients": {"iron_mg": 1.5, "potassium_mg": 290.0, "vitamin_a_iu": 280.0}
        },
        "allergens": ["dairy"],
        "source": "USDA FoodData Central & ICMR / FDC ID: 171302",
        "reference_id": "FDC-171302",
        "synonyms": ["chicken tikka masala", "butter chicken", "chicken gravy", "murgh curry"]
    }
}


def find_matching_food_data(query: str) -> Optional[Dict[str, Any]]:
    """
    Search verified database by exact match or normalized synonym containment.
    """
    if not query:
        return None
    normalized = query.lower().strip()
    
    # Direct match
    if normalized in VERIFIED_FOOD_DATABASE:
        return VERIFIED_FOOD_DATABASE[normalized]
        
    # Search synonyms and canonical names
    for key, data in VERIFIED_FOOD_DATABASE.items():
        if normalized == key or normalized == data["canonical_name"].lower():
            return data
        for synonym in data.get("synonyms", []):
            if synonym == normalized or synonym in normalized or normalized in synonym:
                return data
                
    # Partial token matching
    query_tokens = set(normalized.split())
    best_match = None
    max_overlap = 0
    for key, data in VERIFIED_FOOD_DATABASE.items():
        key_tokens = set(key.split())
        overlap = len(query_tokens.intersection(key_tokens))
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = data
            
    if max_overlap >= 1:
        return best_match
        
    return None
