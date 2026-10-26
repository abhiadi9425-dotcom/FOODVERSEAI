export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface UserProfile {
  id?: string;
  user_id?: string;
  age?: number;
  height_cm?: number;
  weight_kg?: number;
  activity_level: string;
  dietary_pattern: string;
  allergies: string[];
  restrictions: string[];
  goal: string;
  cuisine_preferences: string[];
  budget_range: string;
  meals_per_day: number;
  preferred_foods?: string[];
  avoided_foods?: string[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface FoodAnalysis {
  id?: string;
  food_name: string;
  alternate_names: string[];
  confidence?: number | null;
  serving_size_g: number;
  serving_unit: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
  sugar_g: number;
  sodium_mg: number;
  micronutrients: Record<string, number>;
  data_source: string;
  is_estimate: boolean;
  notes?: string | null;
  image_url?: string | null;
  created_at?: string;
}

export interface VerifiedDatabaseItem {
  key: string;
  name: string;
  category: string;
  default_serving_g: number;
  serving_description: string;
  calories_per_100g: number;
  allergens: string[];
  source: string;
}

export interface FreshnessAssessment {
  id?: string;
  image_url: string;
  food_category: string;
  assessment_category: string; // "No obvious visual spoilage detected" | "Visible quality concerns" | "Potential spoilage indicators"
  confidence?: number | null;
  visual_observations: string[];
  recommendations: string[];
  safety_disclaimer: string;
  provider_used: string;
  is_live_ai: boolean;
  created_at?: string;
}

export interface HygieneFinding {
  id?: string;
  timestamp_s: number;
  category: string;
  observation: string;
  severity: "Low" | "Medium" | "High" | string;
  confidence?: number | null;
  frame_image_url?: string | null;
}

export interface HygieneReport {
  id?: string;
  video_url: string;
  video_duration_s?: number | null;
  total_frames_analyzed: number;
  overall_summary: string;
  overall_risk_level: "Low" | "Moderate" | "High" | string;
  findings: HygieneFinding[];
  practical_recommendations: string[];
  disclaimer: string;
  created_at?: string;
}

export interface RecipeIngredient {
  item: string;
  quantity: string;
  checked?: boolean;
}

export interface RecipeSubstitution {
  original: string;
  alternative: string;
  reason: string;
}

export interface Recipe {
  id?: string;
  title: string;
  description?: string;
  prep_time_min: number;
  cook_time_min: number;
  servings: number;
  cuisine: string;
  difficulty: string;
  ingredients: RecipeIngredient[];
  instructions: string[];
  substitutions: RecipeSubstitution[];
  allergens: string[];
  estimated_nutrition: {
    calories_per_serving?: number;
    protein_g?: number;
    carbs_g?: number;
    fat_g?: number;
    fiber_g?: number;
  };
  food_safety_notes?: string;
  created_at?: string;
}

export interface PlannedMeal {
  id?: string;
  meal_plan_id?: string;
  day_name: string;
  meal_type: string;
  recipe_name: string;
  serving_size: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  ingredients: string[];
  instructions?: string;
  is_completed: boolean;
}

export interface GroceryItem {
  name: string;
  quantity: string;
  purchased: boolean;
}

export interface GroceryCategory {
  category: string;
  items: GroceryItem[];
}

export interface MealPlan {
  id: string;
  user_id: string;
  title: string;
  plan_type: string;
  start_date?: string;
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  grocery_list: GroceryCategory[];
  notes?: string;
  meals: PlannedMeal[];
  created_at: string;
}

export interface ChatMessage {
  id?: string;
  sender: "user" | "assistant" | "system";
  content: string;
  modality?: string;
  created_at?: string;
}

export interface ProviderStatus {
  active_provider: string;
  groq_configured?: boolean;
  gemini_configured: boolean;
  openai_configured: boolean;
  usda_live_configured: boolean;
  verified_reference_db: string;
}
