import React, { useState, useEffect } from "react";
import {
  CalendarDays,
  Sparkles,
  CheckCircle2,
  Circle,
  ShoppingCart,
  ShieldCheck,
  ChevronRight,
  Flame,
  Plus,
  Trash2,
  Info,
} from "lucide-react";
import { Button } from "../../components/common/Button";
import { Card } from "../../components/common/Card";
import { Badge } from "../../components/common/Badge";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { api } from "../../api/client";
import { MealPlan, PlannedMeal } from "../../types";
import { useAuth } from "../../context/AuthContext";

export const MealPlannerPage: React.FC = () => {
  const { profile, isAuthenticated, openAuthModal } = useAuth();

  // Generator settings
  const [planType, setPlanType] = useState<"Daily" | "Weekly">("Weekly");
  const [days, setDays] = useState(7);
  const [mealsPerDay, setMealsPerDay] = useState(3);
  const [dietaryPattern, setDietaryPattern] = useState(profile?.dietary_pattern || "omnivore");
  const [allergies, setAllergies] = useState<string[]>(profile?.allergies || []);
  const [goal, setGoal] = useState(profile?.goal || "healthy_eating");
  const [allergyInput, setAllergyInput] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activePlan, setActivePlan] = useState<MealPlan | null>(null);
  const [activeDay, setActiveDay] = useState<string>("Monday");
  const [savedPlans, setSavedPlans] = useState<MealPlan[]>([]);
  const [groceryChecks, setGroceryChecks] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (profile) {
      setDietaryPattern(profile.dietary_pattern || "omnivore");
      setAllergies(profile.allergies || []);
      setGoal(profile.goal || "healthy_eating");
      setMealsPerDay(profile.meals_per_day || 3);
    }
  }, [profile]);

  useEffect(() => {
    if (isAuthenticated) {
      loadSavedPlans();
    }
  }, [isAuthenticated]);

  const loadSavedPlans = async () => {
    try {
      const plans = await api.getMealPlans();
      setSavedPlans(plans);
      if (plans.length > 0 && !activePlan) {
        setActivePlan(plans[0]);
      }
    } catch {
      // Ignored
    }
  };

  const handleGeneratePlan = async () => {
    if (!isAuthenticated) {
      openAuthModal("login");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const generated = await api.generateMealPlan({
        plan_type: planType,
        days: planType === "Weekly" ? 7 : 1,
        meals_per_day: mealsPerDay,
        dietary_pattern: dietaryPattern,
        allergies,
        goal,
      });

      setActivePlan(generated);
      setSavedPlans([generated, ...savedPlans]);
      if (generated.meals?.length > 0) {
        setActiveDay(generated.meals[0].day_name);
      }
    } catch (err: any) {
      setError(err.message || "Failed to generate meal plan.");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleMeal = async (meal: PlannedMeal) => {
    if (!meal.id) return;
    try {
      const updated = await api.toggleMealStatus(meal.id, !meal.is_completed);
      if (activePlan) {
        setActivePlan({
          ...activePlan,
          meals: activePlan.meals.map((m) => (m.id === meal.id ? updated : m)),
        });
      }
    } catch {
      // Ignored
    }
  };

  const toggleGroceryItem = (itemKey: string) => {
    setGroceryChecks((prev) => ({
      ...prev,
      [itemKey]: !prev[itemKey],
    }));
  };

  const addAllergy = (e: React.FormEvent) => {
    e.preventDefault();
    if (!allergyInput.trim()) return;
    const item = allergyInput.trim();
    if (!allergies.includes(item)) {
      setAllergies([...allergies, item]);
    }
    setAllergyInput("");
  };

  const removeAllergy = (item: string) => {
    setAllergies(allergies.filter((a) => a !== item));
  };

  // Extract unique days present in the active plan
  const planDays = activePlan
    ? Array.from(new Set(activePlan.meals.map((m) => m.day_name)))
    : [];

  const currentDayMeals = activePlan
    ? activePlan.meals.filter((m) => m.day_name === activeDay)
    : [];

  const dayTotalCalories = currentDayMeals.reduce((acc, m) => acc + m.calories, 0);
  const dayTotalProtein = currentDayMeals.reduce((acc, m) => acc + m.protein_g, 0);
  const dayTotalCarbs = currentDayMeals.reduce((acc, m) => acc + m.carbs_g, 0);
  const dayTotalFat = currentDayMeals.reduce((acc, m) => acc + m.fat_g, 0);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">
          <CalendarDays className="w-4 h-4" />
          <span>Precision Dietetics & Zero-Allergen Safety</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
          Personalized Meal Planner
        </h1>
        <p className="text-xs sm:text-sm text-gray-500 mt-1 max-w-2xl">
          Create structured daily and weekly meal plans with derived ingredient calories,
          strict zero-tolerance allergen exclusions, and organized grocery lists.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Preferences Form (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <Card className="p-6 space-y-4">
            <h2 className="text-sm font-bold text-gray-900 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-600" />
              <span>Plan Configuration</span>
            </h2>

            {/* Plan Type & Meals Count */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Schedule
                </label>
                <select
                  value={planType}
                  onChange={(e) => setPlanType(e.target.value as "Daily" | "Weekly")}
                  className="w-full text-xs rounded-xl border border-gray-200 p-2 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="Weekly">7-Day Weekly Plan</option>
                  <option value="Daily">1-Day Focus Plan</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Meals Per Day
                </label>
                <select
                  value={mealsPerDay}
                  onChange={(e) => setMealsPerDay(Number(e.target.value))}
                  className="w-full text-xs rounded-xl border border-gray-200 p-2 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value={3}>3 (Breakfast, Lunch, Dinner)</option>
                  <option value={4}>4 (+ Afternoon Snack)</option>
                </select>
              </div>
            </div>

            {/* Dietary Pattern */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                Dietary Pattern
              </label>
              <select
                value={dietaryPattern}
                onChange={(e) => setDietaryPattern(e.target.value)}
                className="w-full text-xs rounded-xl border border-gray-200 p-2 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="omnivore">Omnivore (Balanced)</option>
                <option value="vegetarian">Vegetarian (Lacto-Ovo)</option>
                <option value="vegan">Vegan (Strictly Plant-Based)</option>
                <option value="pescatarian">Pescatarian (Fish & Plants)</option>
                <option value="sattvic">Sattvic / Pure Vegetarian</option>
                <option value="keto">Ketogenic (Low Carb)</option>
              </select>
            </div>

            {/* Primary Goal */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                Nutrition & Fitness Goal
              </label>
              <select
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                className="w-full text-xs rounded-xl border border-gray-200 p-2 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="healthy_eating">General Healthy Eating & Vitality</option>
                <option value="muscle_gain">Muscle Synthesis & High Protein</option>
                <option value="weight_loss">Calorie Deficit / Fat Loss</option>
                <option value="maintenance">Metabolic Maintenance</option>
                <option value="diabetic_friendly">Low Glycemic & Blood Sugar Stability</option>
              </select>
            </div>

            {/* Strict Allergies Filter */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1 flex items-center justify-between">
                <span>Strict Excluded Allergies</span>
                <span className="text-[10px] text-rose-700 font-bold uppercase">
                  Zero Tolerance
                </span>
              </label>
              <form onSubmit={addAllergy} className="flex gap-2 mb-2">
                <input
                  type="text"
                  placeholder="e.g. Peanuts, Shellfish, Gluten, Soy"
                  value={allergyInput}
                  onChange={(e) => setAllergyInput(e.target.value)}
                  className="flex-1 text-xs rounded-xl border border-gray-200 px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
                <Button type="submit" variant="secondary" size="sm" icon={<Plus className="w-3.5 h-3.5" />}>
                  Add
                </Button>
              </form>
              <div className="flex flex-wrap gap-1.5">
                {allergies.map((a) => (
                  <span
                    key={a}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs bg-rose-50 border border-rose-200 text-rose-900 font-medium"
                  >
                    <span>{a}</span>
                    <button
                      type="button"
                      onClick={() => removeAllergy(a)}
                      className="text-rose-600 hover:text-rose-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
                {allergies.length === 0 && (
                  <p className="text-[11px] text-gray-400">
                    No active allergies declared. All verified ingredients allowed.
                  </p>
                )}
              </div>
            </div>

            <Button
              variant="primary"
              size="md"
              className="w-full mt-2"
              onClick={handleGeneratePlan}
              loading={loading}
              icon={<CalendarDays className="w-4 h-4" />}
            >
              Generate Precision Plan
            </Button>

            {error && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2">
                <Info className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{error}</span>
              </div>
            )}
          </Card>

          {/* Past Plans Selector */}
          {savedPlans.length > 0 && (
            <Card className="p-6">
              <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center justify-between">
                <span>Saved Meal Plans</span>
                <span className="text-xs text-gray-400">{savedPlans.length} plans</span>
              </h3>
              <div className="divide-y divide-gray-100 max-h-48 overflow-y-auto">
                {savedPlans.map((p) => (
                  <div
                    key={p.id}
                    className="py-2.5 flex items-center justify-between text-xs"
                  >
                    <div>
                      <p className="font-semibold text-gray-900">{p.title}</p>
                      <p className="text-[11px] text-gray-400">
                        {p.plan_type} • {p.meals?.length || 0} meals
                      </p>
                    </div>
                    <Button
                      variant={activePlan?.id === p.id ? "secondary" : "ghost"}
                      size="sm"
                      onClick={() => {
                        setActivePlan(p);
                        if (p.meals?.length > 0) setActiveDay(p.meals[0].day_name);
                      }}
                    >
                      {activePlan?.id === p.id ? "Active" : "Load"}
                    </Button>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Right Column: Active Plan View (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {loading ? (
            <Card className="p-12">
              <LoadingSpinner
                message="Calculating daily macro targets and building strict allergen-free meal plan..."
                size="lg"
              />
            </Card>
          ) : activePlan ? (
            <div className="space-y-6">
              <Card className="p-6 space-y-6">
                {/* Plan Title & Averages */}
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-4 border-b border-gray-100">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h2 className="text-xl font-extrabold text-gray-900">
                        {activePlan.title}
                      </h2>
                      <Badge variant="success" size="sm">
                        {activePlan.plan_type}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-500">
                      Derived from component USDA laboratory nutritional composition
                    </p>
                  </div>

                  <div className="text-right">
                    <span className="text-2xl font-black text-emerald-800">
                      {Math.round(dayTotalCalories)}
                    </span>
                    <span className="text-xs text-gray-500 block uppercase font-semibold">
                      {activeDay} Calories (kcal)
                    </span>
                  </div>
                </div>

                {/* Day Navigation Tabs */}
                {planDays.length > 1 && (
                  <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
                    {planDays.map((day) => (
                      <button
                        key={day}
                        onClick={() => setActiveDay(day)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
                          activeDay === day
                            ? "bg-emerald-700 text-white shadow-sm"
                            : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                        }`}
                      >
                        {day}
                      </button>
                    ))}
                  </div>
                )}

                {/* Daily Macronutrient Tally */}
                <div className="grid grid-cols-4 gap-2.5 p-3 rounded-xl bg-gray-50 border border-gray-100 text-center text-xs">
                  <div>
                    <span className="text-[11px] text-gray-400 uppercase block font-semibold">
                      Calories
                    </span>
                    <span className="font-bold text-gray-900">{Math.round(dayTotalCalories)}</span>
                  </div>
                  <div>
                    <span className="text-[11px] text-emerald-700 uppercase block font-semibold">
                      Protein
                    </span>
                    <span className="font-bold text-emerald-800">{Math.round(dayTotalProtein)}g</span>
                  </div>
                  <div>
                    <span className="text-[11px] text-amber-700 uppercase block font-semibold">
                      Carbs
                    </span>
                    <span className="font-bold text-amber-800">{Math.round(dayTotalCarbs)}g</span>
                  </div>
                  <div>
                    <span className="text-[11px] text-orange-700 uppercase block font-semibold">
                      Fats
                    </span>
                    <span className="font-bold text-orange-800">{Math.round(dayTotalFat)}g</span>
                  </div>
                </div>

                {/* Meals for Selected Day */}
                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                    Meals for {activeDay} ({currentDayMeals.length})
                  </h3>
                  <div className="space-y-3">
                    {currentDayMeals.map((meal) => (
                      <div
                        key={meal.id || meal.recipe_name}
                        className={`p-4 rounded-xl border transition-all ${
                          meal.is_completed
                            ? "bg-gray-50/80 border-gray-200 opacity-60"
                            : "bg-white border-gray-100 shadow-subtle"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex items-start gap-3">
                            <button
                              onClick={() => handleToggleMeal(meal)}
                              className="mt-0.5 text-emerald-600 hover:text-emerald-800"
                            >
                              {meal.is_completed ? (
                                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                              ) : (
                                <Circle className="w-5 h-5 text-gray-300" />
                              )}
                            </button>
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <Badge variant="neutral" size="sm">
                                  {meal.meal_type}
                                </Badge>
                                <span className={`text-sm font-bold text-gray-900 ${meal.is_completed ? "line-through text-gray-500" : ""}`}>
                                  {meal.recipe_name}
                                </span>
                              </div>
                              <p className="text-xs text-gray-500">
                                {meal.serving_size} • {meal.calories} kcal • P: {meal.protein_g}g | C: {meal.carbs_g}g | F: {meal.fat_g}g
                              </p>
                              {meal.ingredients?.length > 0 && (
                                <div className="text-[11px] text-gray-600 pt-1">
                                  <strong>Key Ingredients:</strong> {Array.isArray(meal.ingredients) ? meal.ingredients.join(", ") : JSON.stringify(meal.ingredients)}
                                </div>
                              )}
                              {meal.instructions && (
                                <p className="text-[11px] text-gray-500 italic pt-1">
                                  {meal.instructions}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Categorized Grocery List */}
                {activePlan.grocery_list?.length > 0 && (
                  <div className="space-y-3 pt-4 border-t border-gray-100">
                    <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider flex items-center gap-2">
                      <ShoppingCart className="w-4 h-4 text-emerald-700" />
                      <span>Consolidated Weekly Grocery Checklist</span>
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {activePlan.grocery_list.map((cat, cIdx) => (
                        <div
                          key={cIdx}
                          className="p-3 rounded-xl bg-gray-50/80 border border-gray-100 text-xs space-y-2"
                        >
                          <span className="font-bold text-emerald-900 block border-b border-gray-200/60 pb-1">
                            {cat.category}
                          </span>
                          <div className="space-y-1.5">
                            {cat.items.map((item, iIdx) => {
                              const key = `${cat.category}-${item.name}-${iIdx}`;
                              const checked = groceryChecks[key] || false;
                              return (
                                <div
                                  key={key}
                                  onClick={() => toggleGroceryItem(key)}
                                  className={`flex items-center justify-between cursor-pointer select-none ${
                                    checked ? "line-through text-gray-400" : "text-gray-700"
                                  }`}
                                >
                                  <span>{item.name}</span>
                                  <span className="text-[11px] text-gray-400 font-medium">
                                    {item.quantity}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            </div>
          ) : (
            <Card className="p-12 text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-purple-50 border border-purple-100 flex items-center justify-center mx-auto text-purple-700">
                <CalendarDays className="w-8 h-8" />
              </div>
              <div className="max-w-md mx-auto">
                <h3 className="text-base font-bold text-gray-900">
                  Ready to Plan Meals
                </h3>
                <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">
                  Configure your dietary pattern, schedule, and allergy exclusions on the left to generate an authentic, nutrient-balanced meal schedule.
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
