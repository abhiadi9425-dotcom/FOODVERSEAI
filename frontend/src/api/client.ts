import {
  AuthResponse,
  User,
  UserProfile,
  FoodAnalysis,
  VerifiedDatabaseItem,
  FreshnessAssessment,
  HygieneReport,
  Recipe,
  MealPlan,
  PlannedMeal,
  ProviderStatus,
} from "../types";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  private getHeaders(isFormData: boolean = false): HeadersInit {
    const headers: Record<string, string> = {};
    if (!isFormData) {
      headers["Content-Type"] = "application/json";
    }
    try {
      if (typeof window !== "undefined" && window.localStorage) {
        const token = window.localStorage.getItem("foodverse_token");
        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }
      }
    } catch {
      // Ignored
    }
    return headers;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const isFormData = options.body instanceof FormData;
    const headers = { ...this.getHeaders(isFormData), ...(options.headers as Record<string, string>) };

    const url = `${BASE_URL}${endpoint}`;
    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
      let errorMessage = `Request failed (${response.status})`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
        }
      } catch {
        // Fallback to status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  // --- Auth ---
  async register(data: { email: string; password: string; full_name?: string }): Promise<AuthResponse> {
    return this.request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async login(data: { email: string; password: string }): Promise<AuthResponse> {
    return this.request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getMe(): Promise<{ user: User; profile: UserProfile }> {
    return this.request<{ user: User; profile: UserProfile }>("/auth/me");
  }

  // --- Profile ---
  async getProfile(): Promise<UserProfile> {
    return this.request<UserProfile>("/profile");
  }

  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    return this.request<UserProfile>("/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteAccount(): Promise<{ message: string }> {
    return this.request<{ message: string }>("/profile/account", {
      method: "DELETE",
    });
  }

  // --- Food Scanner ---
  async getVerifiedDatabaseItems(): Promise<VerifiedDatabaseItem[]> {
    return this.request<VerifiedDatabaseItem[]>("/food/database-items");
  }

  async analyzeFood(formData: FormData): Promise<FoodAnalysis> {
    return this.request<FoodAnalysis>("/food/analyze", {
      method: "POST",
      body: formData,
    });
  }

  async recalculateNutrition(food_name: string, serving_size_g: number): Promise<FoodAnalysis> {
    return this.request<FoodAnalysis>("/food/recalculate", {
      method: "POST",
      body: JSON.stringify({ food_name, serving_size_g, serving_unit: "grams" }),
    });
  }

  async getFoodHistory(): Promise<FoodAnalysis[]> {
    return this.request<FoodAnalysis[]>("/food/history");
  }

  async getFoodAnalysisDetail(id: string): Promise<FoodAnalysis> {
    return this.request<FoodAnalysis>(`/food/history/${id}`);
  }

  async deleteFoodAnalysis(id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/food/history/${id}`, {
      method: "DELETE",
    });
  }

  // --- Freshness ---
  async analyzeFreshness(formData: FormData): Promise<FreshnessAssessment> {
    return this.request<FreshnessAssessment>("/freshness/analyze", {
      method: "POST",
      body: formData,
    });
  }

  async getFreshnessHistory(): Promise<FreshnessAssessment[]> {
    return this.request<FreshnessAssessment[]>("/freshness/history");
  }

  // --- Hygiene ---
  async analyzeHygieneVideo(formData: FormData): Promise<HygieneReport> {
    return this.request<HygieneReport>("/hygiene/analyze", {
      method: "POST",
      body: formData,
    });
  }

  async getHygieneHistory(): Promise<HygieneReport[]> {
    return this.request<HygieneReport[]>("/hygiene/history");
  }

  async getHygieneReport(id: string): Promise<HygieneReport> {
    return this.request<HygieneReport>(`/hygiene/reports/${id}`);
  }

  // --- Cooking ---
  async generateRecipe(data: {
    query: string;
    ingredients?: string[];
    dietary_restrictions?: string[];
    cuisine?: string;
    servings?: number;
    cooking_time_min?: number;
  }): Promise<Recipe> {
    return this.request<Recipe>("/cooking/recipes", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async chatRecipe(data: {
    message: string;
    current_recipe?: Recipe | null;
    conversation_history?: Array<{ role: string; content: string }>;
  }): Promise<{ reply: string }> {
    return this.request<{ reply: string }>("/cooking/chat", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async saveRecipe(recipe: Partial<Recipe>): Promise<Recipe> {
    return this.request<Recipe>("/cooking/save", {
      method: "POST",
      body: JSON.stringify(recipe),
    });
  }

  async getSavedRecipes(search?: string): Promise<Recipe[]> {
    const query = search ? `?search=${encodeURIComponent(search)}` : "";
    return this.request<Recipe[]>(`/cooking/recipes${query}`);
  }

  async deleteRecipe(id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/cooking/recipes/${id}`, {
      method: "DELETE",
    });
  }

  // --- Meal Plans ---
  async generateMealPlan(data: {
    title?: string;
    plan_type?: string;
    days?: number;
    meals_per_day?: number;
    dietary_pattern?: string;
    allergies?: string[];
    restrictions?: string[];
    goal?: string;
    cuisine_preferences?: string[];
  }): Promise<MealPlan> {
    return this.request<MealPlan>("/meal-plans/generate", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getMealPlans(): Promise<MealPlan[]> {
    return this.request<MealPlan[]>("/meal-plans");
  }

  async getMealPlanDetail(id: string): Promise<MealPlan> {
    return this.request<MealPlan>(`/meal-plans/${id}`);
  }

  async toggleMealStatus(meal_id: string, is_completed: boolean): Promise<PlannedMeal> {
    return this.request<PlannedMeal>(`/meal-plans/meals/${meal_id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ is_completed }),
    });
  }

  async deleteMealPlan(id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/meal-plans/${id}`, {
      method: "DELETE",
    });
  }

  // --- Multimodal Assistant ---
  async chatAssistant(data: {
    message: string;
    conversation_id?: string | null;
    modality?: string;
    context_data?: Record<string, unknown> | null;
  }): Promise<{ reply: string; conversation_id?: string }> {
    return this.request<{ reply: string; conversation_id?: string }>("/assistant/chat", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async transcribeAudio(formData: FormData): Promise<{ transcript: string; mime_type: string }> {
    return this.request<{ transcript: string; mime_type: string }>("/assistant/transcribe", {
      method: "POST",
      body: formData,
    });
  }

  async getConversations(): Promise<Array<{ id: string; title: string; created_at: string }>> {
    return this.request<Array<{ id: string; title: string; created_at: string }>>("/assistant/conversations");
  }

  // --- System Health ---
  async getHealth(): Promise<{
    status: string;
    database_connected: boolean;
    ai_providers: ProviderStatus;
    version: string;
  }> {
    return this.request<{
      status: string;
      database_connected: boolean;
      ai_providers: ProviderStatus;
      version: string;
    }>("/health");
  }
}

export const api = new ApiClient();
