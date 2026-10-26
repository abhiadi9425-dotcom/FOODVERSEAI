import React, { useState, useEffect } from "react";
import {
  History,
  ScanLine,
  Apple,
  Video,
  ChefHat,
  CalendarDays,
  Trash2,
  Clock,
  Sparkles,
  ChevronRight,
} from "lucide-react";
import { Button } from "../../components/common/Button";
import { Card } from "../../components/common/Card";
import { Badge } from "../../components/common/Badge";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { api } from "../../api/client";
import { FoodAnalysis, FreshnessAssessment, HygieneReport, Recipe, MealPlan } from "../../types";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";

export const HistoryPage: React.FC = () => {
  const { isAuthenticated, openAuthModal } = useAuth();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<"food" | "freshness" | "hygiene" | "recipes" | "plans">("food");
  const [loading, setLoading] = useState(true);

  const [foodHistory, setFoodHistory] = useState<FoodAnalysis[]>([]);
  const [freshnessHistory, setFreshnessHistory] = useState<FreshnessAssessment[]>([]);
  const [hygieneHistory, setHygieneHistory] = useState<HygieneReport[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([]);

  useEffect(() => {
    if (isAuthenticated) {
      loadAllHistory();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const loadAllHistory = async () => {
    setLoading(true);
    try {
      const [foods, fresh, hygs, recs, plans] = await Promise.allSettled([
        api.getFoodHistory(),
        api.getFreshnessHistory(),
        api.getHygieneHistory(),
        api.getSavedRecipes(),
        api.getMealPlans(),
      ]);

      if (foods.status === "fulfilled") setFoodHistory(foods.value);
      if (fresh.status === "fulfilled") setFreshnessHistory(fresh.value);
      if (hygs.status === "fulfilled") setHygieneHistory(hygs.value);
      if (recs.status === "fulfilled") setRecipes(recs.value);
      if (plans.status === "fulfilled") setMealPlans(plans.value);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFood = async (id: string) => {
    try {
      await api.deleteFoodAnalysis(id);
      setFoodHistory(foodHistory.filter((f) => f.id !== id));
    } catch {
      // Ignored
    }
  };

  const handleDeleteRecipe = async (id?: string) => {
    if (!id) return;
    try {
      await api.deleteRecipe(id);
      setRecipes(recipes.filter((r) => r.id !== id));
    } catch {
      // Ignored
    }
  };

  const handleDeleteMealPlan = async (id: string) => {
    try {
      await api.deleteMealPlan(id);
      setMealPlans(mealPlans.filter((p) => p.id !== id));
    } catch {
      // Ignored
    }
  };

  if (!isAuthenticated) {
    return (
      <Card className="p-12 text-center space-y-4 max-w-lg mx-auto">
        <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-800 flex items-center justify-center mx-auto">
          <History className="w-6 h-6" />
        </div>
        <h2 className="text-base font-bold text-gray-900">Sign in to Access Private History</h2>
        <p className="text-xs text-gray-500">
          All your food scans, freshness audits, saved culinary recipes, and meal plans are private to your authenticated account.
        </p>
        <Button variant="primary" size="md" onClick={() => openAuthModal("login")}>
          Sign In
        </Button>
      </Card>
    );
  }

  const tabs = [
    { id: "food", label: "Food Analyses", icon: ScanLine, count: foodHistory.length },
    { id: "freshness", label: "Freshness Checks", icon: Apple, count: freshnessHistory.length },
    { id: "hygiene", label: "Hygiene Audits", icon: Video, count: hygieneHistory.length },
    { id: "recipes", label: "Saved Recipes", icon: ChefHat, count: recipes.length },
    { id: "plans", label: "Meal Plans", icon: CalendarDays, count: mealPlans.length },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">
          <History className="w-4 h-4" />
          <span>Audit Trail & Records</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
          History & Saved Intelligence
        </h1>
        <p className="text-xs sm:text-sm text-gray-500 mt-1">
          Access and manage your private multimodal food logs, past audits, recipes, and dietary schedules.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-gray-200 overflow-x-auto pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
                isActive
                  ? "bg-emerald-700 text-white shadow-sm"
                  : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${isActive ? "bg-emerald-800 text-emerald-100" : "bg-gray-100 text-gray-500"}`}>
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Tab Contents */}
      {loading ? (
        <Card className="p-12">
          <LoadingSpinner message="Retrieving your private records..." />
        </Card>
      ) : (
        <div>
          {/* 1. Food Analyses */}
          {activeTab === "food" && (
            <Card className="p-6">
              <div className="divide-y divide-gray-100">
                {foodHistory.map((item) => (
                  <div key={item.id} className="py-4 flex items-center justify-between gap-4 text-xs">
                    <div>
                      <h3 className="text-sm font-bold text-gray-900">{item.food_name}</h3>
                      <p className="text-gray-500 mt-0.5">
                        {item.serving_size_g}g • {Math.round(item.calories)} kcal • P: {item.protein_g}g | C: {item.carbs_g}g | F: {item.fat_g}g
                      </p>
                      <p className="text-[11px] text-gray-400 mt-0.5">
                        Source: {item.data_source}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm" onClick={() => navigate("/scanner")}>
                        Open Scanner
                      </Button>
                      <button
                        onClick={() => item.id && handleDeleteFood(item.id)}
                        className="text-gray-400 hover:text-rose-600 p-1.5 rounded-lg"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
                {foodHistory.length === 0 && (
                  <p className="text-xs text-gray-400 py-8 text-center">
                    No food analyses recorded yet. Scan your first meal in Food Scanner!
                  </p>
                )}
              </div>
            </Card>
          )}

          {/* 2. Freshness Checks */}
          {activeTab === "freshness" && (
            <Card className="p-6">
              <div className="divide-y divide-gray-100">
                {freshnessHistory.map((item, idx) => (
                  <div key={item.id || idx} className="py-4 flex items-center justify-between gap-4 text-xs">
                    <div>
                      <h3 className="text-sm font-bold text-gray-900">{item.food_category}</h3>
                      <p className="text-gray-600 mt-0.5 font-medium">
                        {item.assessment_category}
                      </p>
                      <p className="text-[11px] text-gray-400 mt-0.5">
                        {item.visual_observations?.join(" • ")}
                      </p>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => navigate("/freshness")}>
                      Inspect
                    </Button>
                  </div>
                ))}
                {freshnessHistory.length === 0 && (
                  <p className="text-xs text-gray-400 py-8 text-center">
                    No freshness inspections recorded yet.
                  </p>
                )}
              </div>
            </Card>
          )}

          {/* 3. Hygiene Audits */}
          {activeTab === "hygiene" && (
            <Card className="p-6">
              <div className="divide-y divide-gray-100">
                {hygieneHistory.map((item, idx) => (
                  <div key={item.id || idx} className="py-4 flex items-center justify-between gap-4 text-xs">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-bold text-gray-900">
                          Kitchen Video Audit
                        </h3>
                        <Badge variant="warning" size="sm">
                          {item.overall_risk_level} Risk
                        </Badge>
                      </div>
                      <p className="text-gray-600 mt-0.5">
                        {item.total_frames_analyzed} frames analyzed • {item.video_duration_s}s
                      </p>
                      <p className="text-[11px] text-gray-400 mt-0.5 max-w-lg">
                        {item.overall_summary}
                      </p>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => navigate("/hygiene")}>
                      View Findings
                    </Button>
                  </div>
                ))}
                {hygieneHistory.length === 0 && (
                  <p className="text-xs text-gray-400 py-8 text-center">
                    No video hygiene audits recorded yet.
                  </p>
                )}
              </div>
            </Card>
          )}

          {/* 4. Saved Recipes */}
          {activeTab === "recipes" && (
            <Card className="p-6">
              <div className="divide-y divide-gray-100">
                {recipes.map((r) => (
                  <div key={r.id} className="py-4 flex items-center justify-between gap-4 text-xs">
                    <div>
                      <h3 className="text-sm font-bold text-gray-900">{r.title}</h3>
                      <p className="text-gray-500 mt-0.5">
                        {r.cuisine} • {r.prep_time_min + r.cook_time_min} mins • {r.servings} Servings
                      </p>
                      {r.description && (
                        <p className="text-[11px] text-gray-400 mt-0.5 line-clamp-1">
                          {r.description}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm" onClick={() => navigate("/cooking")}>
                        Cook Dish
                      </Button>
                      <button
                        onClick={() => handleDeleteRecipe(r.id)}
                        className="text-gray-400 hover:text-rose-600 p-1.5 rounded-lg"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
                {recipes.length === 0 && (
                  <p className="text-xs text-gray-400 py-8 text-center">
                    No saved recipes in your collection.
                  </p>
                )}
              </div>
            </Card>
          )}

          {/* 5. Meal Plans */}
          {activeTab === "plans" && (
            <Card className="p-6">
              <div className="divide-y divide-gray-100">
                {mealPlans.map((p) => (
                  <div key={p.id} className="py-4 flex items-center justify-between gap-4 text-xs">
                    <div>
                      <h3 className="text-sm font-bold text-gray-900">{p.title}</h3>
                      <p className="text-gray-500 mt-0.5">
                        {p.plan_type} • {p.meals?.length || 0} meals • Approx. {Math.round(p.total_calories)} kcal
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm" onClick={() => navigate("/meal-planner")}>
                        View Plan
                      </Button>
                      <button
                        onClick={() => handleDeleteMealPlan(p.id)}
                        className="text-gray-400 hover:text-rose-600 p-1.5 rounded-lg"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
                {mealPlans.length === 0 && (
                  <p className="text-xs text-gray-400 py-8 text-center">
                    No meal plans generated yet.
                  </p>
                )}
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};
