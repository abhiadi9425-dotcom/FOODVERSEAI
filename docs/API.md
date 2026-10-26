# FoodVerse AI — REST API Documentation

Base URL: `http://localhost:8000/api/v1`  
Interactive OpenAPI Swagger Docs: `http://localhost:8000/docs`  
ReDoc Documentation: `http://localhost:8000/redoc`

---

## Authentication Endpoints (`/auth`)

### 1. Register User
`POST /auth/register`
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "Maya Patel"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": "uuid-v4",
      "email": "user@example.com",
      "full_name": "Maya Patel",
      "is_active": true,
      "created_at": "2026-10-26T00:00:00Z"
    }
  }
  ```

### 2. Login User
`POST /auth/login`
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": { "id": "...", "email": "..." }
  }
  ```

### 3. Get Current User Info
`GET /auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):** Returns user account info and linked profile data.

---

## Food Analysis & Nutrition Endpoints (`/food`)

### 1. Get Verified Database Items
`GET /food/database-items`
- **Response (200 OK):** List of verified food benchmarks from USDA and ICMR tables.

### 2. Analyze Food
`POST /food/analyze`
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `image`: File (optional if food_name provided)
  - `food_name`: String (optional if image provided)
  - `serving_size_g`: Float (default 100.0)
  - `serving_unit`: String ("grams")
- **Response (200 OK):**
  ```json
  {
    "id": "uuid",
    "food_name": "Vegetable Poha",
    "alternate_names": ["Poha", "Flattened Rice"],
    "confidence": 0.94,
    "serving_size_g": 250.0,
    "serving_unit": "grams",
    "calories": 350.0,
    "protein_g": 7.0,
    "carbs_g": 63.5,
    "fat_g": 8.0,
    "fiber_g": 5.2,
    "sugar_g": 3.5,
    "sodium_mg": 700.0,
    "micronutrients": { "iron_mg": 9.5, "vitamin_c_mg": 21.2 },
    "data_source": "USDA / ICMR Food Composition Tables",
    "is_estimate": false,
    "image_url": "/uploads/food_abc123.jpg"
  }
  ```

### 3. Recalculate Nutrition
`POST /food/recalculate`
- **Request Body:**
  ```json
  {
    "food_name": "Vegetable Poha",
    "serving_size_g": 300.0,
    "serving_unit": "grams"
  }
  ```

### 4. Food History
`GET /food/history`
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):** Returns private history records for the authenticated user.

---

## Freshness Assessment (`/freshness`)

### 1. Analyze Freshness
`POST /freshness/analyze`
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `image`: File (Required)
  - `food_category`: String ("Fresh Produce / Fruits", etc.)
- **Response (200 OK):**
  ```json
  {
    "id": "uuid",
    "food_category": "Fresh Produce / Fruits",
    "assessment_category": "No obvious visual spoilage detected",
    "confidence": 0.91,
    "visual_observations": [
      "Firm skin texture with consistent coloration",
      "No visible mycelium or localized bruising"
    ],
    "recommendations": [
      "Wash thoroughly under potable water prior to slicing",
      "Store refrigerated below 4°C"
    ],
    "safety_disclaimer": "Visual assessment cannot detect invisible bacterial pathogens.",
    "provider_used": "Google Gemini (gemini-2.5-flash)",
    "is_live_ai": true
  }
  ```

---

## Kitchen Hygiene Video Monitoring (`/hygiene`)

### 1. Analyze Video
`POST /hygiene/analyze`
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `video`: File (MP4, MOV, max 50MB, max 120s)
  - `interval_seconds`: Float (default 2.0)
- **Response (200 OK):**
  ```json
  {
    "id": "uuid",
    "video_url": "/uploads/hygiene_vid_123.mp4",
    "video_duration_s": 24.5,
    "total_frames_analyzed": 8,
    "overall_summary": "Station cleanliness adhered to with consistent glove protocol.",
    "overall_risk_level": "Low",
    "findings": [
      {
        "timestamp_s": 2.0,
        "category": "Glove Usage",
        "observation": "Food handler wearing clean disposable gloves during garnish assembly.",
        "severity": "Low",
        "confidence": 0.93,
        "frame_image_url": "/uploads/frames/frame_abc_20.jpg"
      }
    ],
    "practical_recommendations": [
      "Maintain 2-hour holding temperature audits"
    ],
    "disclaimer": "This is an AI-assisted frame audit and not an official regulatory inspection."
  }
  ```

---

## Smart Cooking Assistant (`/cooking`)

### 1. Generate Recipe
`POST /cooking/recipes`
- **Request Body:**
  ```json
  {
    "query": "High protein paneer curry",
    "ingredients": ["Paneer", "Bell peppers", "Spices"],
    "dietary_restrictions": ["Vegetarian"],
    "cuisine": "Indian",
    "servings": 2,
    "cooking_time_min": 25
  }
  ```

### 2. Conversational Refinement
`POST /cooking/chat`
- **Request Body:**
  ```json
  {
    "message": "Can I substitute tofu for paneer to make it vegan?",
    "current_recipe": { ... }
  }
  ```

---

## Personalized Meal Planning (`/meal-planner`)

### 1. Generate Meal Plan
`POST /meal-plans/generate`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "title": "Weekly High-Protein Plan",
    "plan_type": "Weekly",
    "days": 7,
    "meals_per_day": 3,
    "dietary_pattern": "vegetarian",
    "allergies": ["peanuts"],
    "goal": "muscle_gain"
  }
  ```

---

## Multimodal Assistant (`/assistant`)

### 1. Chat
`POST /assistant/chat`
- **Request Body:**
  ```json
  {
    "message": "What are optimal protein sources in an Indian vegetarian diet?",
    "modality": "text"
  }
  ```

### 2. Transcribe Audio
`POST /assistant/transcribe`
- **Content-Type:** `multipart/form-data`
- **Form Fields:** `audio`: File (MP3, WAV, M4A, WEBM)
