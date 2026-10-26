# FoodVerse AI — System Architecture

FoodVerse AI is an enterprise-grade multimodal food intelligence platform engineered with a strict decoupled architecture. It separates presentation, core business logic, verified nutritional reference engines, and neural model provider abstractions.

## High-Level Architecture Diagram

```mermaid
graph TD
    User["User (Web / Mobile Browser)"]
    
    subgraph Frontend ["React 18 + TypeScript + Tailwind CSS Frontend"]
        UI["UI Pages & Features"]
        AuthCtx["Auth Context (JWT)"]
        Recharts["Recharts Nutrition Visualizations"]
        ApiClient["Typed API Client"]
    end

    subgraph Backend ["FastAPI Python Backend"]
        Router["Versioned REST API (/api/v1)"]
        AuthDep["JWT & Ownership Isolation Layer"]
        Services["Domain Application Services"]
        
        subgraph DomainServices ["Specialized Services"]
            FoodService["Food Analysis & Portion Scaler"]
            FreshService["Freshness & Spoilage Assessor"]
            HygieneService["Video Keyframe Extractor (OpenCV)"]
            CookingService["Interactive Recipe Engine"]
            MealPlanService["Allergen-Filtered Diet Planner"]
            AudioService["Speech-to-Text Transcriber"]
        end

        subgraph Abstraction ["AI Provider Abstraction Layer"]
            Factory["Provider Factory"]
            Gemini["GeminiProvider (google.genai 2.5 Flash)"]
            OpenAI["OpenAIProvider (GPT-4o + Whisper)"]
            Fallback["RuleBasedFallbackProvider (Transparent Baseline)"]
        end
    end

    subgraph Persistence ["Data & Storage Layer"]
        SQLite["SQLite / PostgreSQL Database"]
        Storage["Local Uploads / S3 Blob Storage"]
        USDA["USDA FoodData Central & ICMR Lab Database"]
    end

    User --> UI
    UI --> AuthCtx
    UI --> Recharts
    UI --> ApiClient
    ApiClient -->|HTTP / JSON / Multipart| Router
    
    Router --> AuthDep
    AuthDep --> Services
    
    Services --> FoodService
    Services --> FreshService
    Services --> HygieneService
    Services --> CookingService
    Services --> MealPlanService
    Services --> AudioService
    
    FoodService --> Abstraction
    FreshService --> Abstraction
    HygieneService --> Abstraction
    CookingService --> Abstraction
    MealPlanService --> Abstraction
    AudioService --> Abstraction

    Factory --> Gemini
    Factory --> OpenAI
    Factory --> Fallback

    FoodService --> USDA
    MealPlanService --> USDA
    Services --> SQLite
    HygieneService --> Storage
    FoodService --> Storage
```

## Core Architectural Principles

1. **Provider Abstraction Layer (`app.services.ai`)**:
   - High-level domain services depend exclusively on `BaseAIProvider` rather than specific SDKs.
   - The active provider is dynamically resolved at runtime via `provider_factory.py`.
   - When no external API key is provided, the system transparently runs in `RuleBasedFallbackProvider` mode rather than hallucinating or pretending live inference took place.

2. **Verified Laboratory Nutrition Pipeline (`app.services.nutrition`)**:
   - Rather than allowing LLMs to guess arbitrary calorie or macro numbers, all nutritional calculations scale deterministically against laboratory composition tables (USDA FoodData Central and ICMR Food Composition Tables).
   - Meal plans aggregate component macronutrients and calories deterministically.

3. **Strict Allergen Exclusion Security**:
   - Allergies (e.g. peanuts, tree nuts, shellfish, dairy, gluten) are treated as zero-tolerance exclusions.
   - Any generated dish containing or referencing declared allergens is automatically filtered or flagged with substitute warnings.

4. **Private Multi-User Data Isolation**:
   - All private resources (`FoodAnalysis`, `FreshnessAssessment`, `HygieneReport`, `SavedRecipe`, `MealPlan`, `Conversation`) enforce strict database-level `user_id` ownership constraints.
   - Users cannot access, view, or delete another user's records by manipulating resource IDs.

5. **OpenCV Keyframe Video Sampling**:
   - Uploaded videos are parsed via `cv2.VideoCapture` with duration and frame limits.
   - Sampled frames are converted to standardized JPEG thumbnails, enabling timestamped visual evidence linking for kitchen hygiene observations.
