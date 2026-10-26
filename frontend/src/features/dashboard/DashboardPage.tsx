import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ScanLine,
  Apple,
  Video,
  ChefHat,
  CalendarDays,
  BotMessageSquare,
  ArrowRight,
  TrendingUp,
  Clock,
  Sparkles,
  Scale,
  Plus,
} from "lucide-react";
import { Button } from "../../components/common/Button";
import { Card } from "../../components/common/Card";
import { Badge } from "../../components/common/Badge";
import { NutritionChart } from "../../components/common/NutritionChart";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { api } from "../../api/client";
import { FoodAnalysis, MealPlan, FreshnessAssessment } from "../../types";
import { useAuth } from "../../context/AuthContext";

export const DashboardPage: React.FC = () => {
  const { user, profile } = useAuth();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [foodHistory, setFoodHistory] = useState<FoodAnalysis[]>([]);
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([]);
  const [freshnessChecks, setFreshnessChecks] = useState<FreshnessAssessment[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [foods, plans, freshness] = await Promise.allSettled([
        api.getFoodHistory(),
        api.getMealPlans(),
        api.getFreshnessHistory(),
      ]);

      if (foods.status === "fulfilled") setFoodHistory(foods.value);
      if (plans.status === "fulfilled") setMealPlans(plans.value);
      if (freshness.status === "fulfilled") setFreshnessChecks(freshness.value);
    } finally {
      setLoading(false);
    }
  };

  // Derive today's recorded nutritional totals from real user scans
  const totalCaloriesScanned = foodHistory.reduce((sum, f) => sum + f.calories, 0);
  const totalProteinScanned = foodHistory.reduce((sum, f) => sum + f.protein_g, 0);
  const totalCarbsScanned = foodHistory.reduce((sum, f) => sum + f.carbs_g, 0);
  const totalFatScanned = foodHistory.reduce((sum, f) => sum + f.fat_g, 0);

  const quickActions = [
    {
      title: "Scan Food",
      desc: "Analyze dishes & USDA nutrients",
      icon: ScanLine,
      color: "bg-emerald-50 text-emerald-700 border-emerald-200",
      path: "/scanner",
    },
    {
      title: "Check Freshness",
      desc: "Surface spoilage visual audit",
      icon: Apple,
      color: "bg-amber-50 text-amber-700 border-amber-200",
      path: "/freshness",
    },
    {
      title: "Hygiene Monitor",
      desc: "Video keyframe station audit",
      icon: Video,
      color: "bg-blue-50 text-blue-700 border-blue-200",
      path: "/hygiene",
    },
    {
      title: "Smart Cooking",
      desc: "Step-by-step recipes from ingredients",
      icon: ChefHat,
      color: "bg-orange-50 text-orange-700 border-orange-200",
      path: "/cooking",
    },
    {
      title: "Meal Planner",
      desc: "Allergen-free daily/weekly plans",
      icon: CalendarDays,
      color: "bg-purple-50 text-purple-700 border-purple-200",
      path: "/meal-planner",
    },
    {
      title: "Multimodal AI",
      desc: "Voice & text intelligence reasoning",
      icon: BotMessageSquare,
      color: "bg-teal-50 text-teal-700 border-teal-200",
      path: "/assistant",
    },
  ];

  if (loading) {
    return (
      <Card className="p-16">
        <LoadingSpinner message="Loading your food intelligence dashboard..." size="lg" />
      </Card>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-emerald-900 to-emerald-800 text-white p-6 sm:p-8 rounded-3xl shadow-elevated">
        <div className="space-y-2">
          <Badge variant="success" size="sm" className="bg-emerald-800/80 border-emerald-700 text-emerald-200">
            Authenticated Profile Active
          </Badge>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome back, {user?.full_name || user?.email.split("@")[0]}
          </h1>
          <p className="text-xs sm:text-sm text-emerald-100/90 max-w-xl leading-relaxed">
            Targeting{" "}
            <span className="font-semibold text-white">
              {profile?.goal?.replace("_", " ") || "healthy eating"}
            </span>{" "}
            with a{" "}
            <span className="font-semibold text-white">
              {profile?.dietary_pattern || "balanced"}
            </span>{" "}
            dietary pattern.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="md"
            onClick={() => navigate("/scanner")}
            icon={<Plus className="w-4 h-4" />}
          >
            New Food Scan
          </Button>
        </div>
      </div>

      {/* Quick Actions Shortcuts */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold text-gray-900 uppercase tracking-wider">
          Quick Actions & Capabilities
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {quickActions.map((qa) => {
            const Icon = qa.icon;
            return (
              <Card
                key={qa.title}
                hover
                onClick={() => navigate(qa.path)}
                className="p-4 flex flex-col items-center text-center space-y-2"
              >
                <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${qa.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-gray-900">{qa.title}</h3>
                  <p className="text-[10px] text-gray-400 mt-0.5 line-clamp-1">{qa.desc}</p>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Real Data Nutrition Overview & Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Scanned Nutrition Totals (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <Card className="p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100">
              <div>
                <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-emerald-700" />
                  <span>Recorded Nutrition Aggregation</span>
                </h3>
                <p className="text-xs text-gray-400 mt-0.5">
                  Calculated from your {foodHistory.length} recorded food scans
                </p>
              </div>

              {foodHistory.length > 0 && (
                <Badge variant="success" size="sm">
                  {Math.round(totalCaloriesScanned)} kcal total
                </Badge>
              )}
            </div>

            {foodHistory.length > 0 ? (
              <div className="space-y-6 pt-2">
                <NutritionChart
                  protein_g={Math.round(totalProteinScanned)}
                  carbs_g={Math.round(totalCarbsScanned)}
                  fat_g={Math.round(totalFatScanned)}
                  calories={totalCaloriesScanned}
                />

                <div className="grid grid-cols-3 gap-3 pt-2 border-t border-gray-100 text-center text-xs">
                  <div className="p-2.5 rounded-xl bg-gray-50">
                    <span className="text-[11px] text-emerald-700 font-semibold uppercase block">
                      Protein
                    </span>
                    <span className="font-bold text-gray-900 text-sm">
                      {Math.round(totalProteinScanned)}g
                    </span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-gray-50">
                    <span className="text-[11px] text-amber-700 font-semibold uppercase block">
                      Carbs
                    </span>
                    <span className="font-bold text-gray-900 text-sm">
                      {Math.round(totalCarbsScanned)}g
                    </span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-gray-50">
                    <span className="text-[11px] text-orange-700 font-semibold uppercase block">
                      Fats
                    </span>
                    <span className="font-bold text-gray-900 text-sm">
                      {Math.round(totalFatScanned)}g
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-8 text-center space-y-3">
                <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center mx-auto">
                  <ScanLine className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-800">
                    No Recorded Food Scans Yet
                  </p>
                  <p className="text-[11px] text-gray-400 mt-1 max-w-xs mx-auto">
                    Scan your first meal or select a verified dish to begin tracking macronutrient and calorie trends.
                  </p>
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => navigate("/scanner")}
                >
                  Go to Food Scanner
                </Button>
              </div>
            )}
          </Card>
        </div>

        {/* Recent Activity Feeds (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Active Meal Plan Shortcut */}
          <Card className="p-6 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                <CalendarDays className="w-4 h-4 text-purple-700" />
                <span>Active Meal Plan</span>
              </h3>
              <Link
                to="/meal-planner"
                className="text-xs font-semibold text-emerald-700 hover:text-emerald-900"
              >
                View All
              </Link>
            </div>

            {mealPlans.length > 0 ? (
              <div className="p-3.5 rounded-xl bg-purple-50/60 border border-purple-100 text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-purple-950">{mealPlans[0].title}</span>
                  <Badge variant="neutral" size="sm">
                    {mealPlans[0].plan_type}
                  </Badge>
                </div>
                <p className="text-[11px] text-purple-900/80">
                  {mealPlans[0].meals?.length || 0} meals planned • Total approx. {Math.round(mealPlans[0].total_calories)} kcal
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full text-purple-950 border-purple-200 hover:bg-purple-100/50 mt-1"
                  onClick={() => navigate("/meal-planner")}
                >
                  Manage Active Plan
                </Button>
              </div>
            ) : (
              <div className="p-4 text-center rounded-xl bg-gray-50 text-xs text-gray-500 space-y-2">
                <p>No active meal plan generated yet.</p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate("/meal-planner")}
                >
                  Create Plan
                </Button>
              </div>
            )}
          </Card>

          {/* Recent Scans List */}
          <Card className="p-6 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                <Clock className="w-4 h-4 text-gray-500" />
                <span>Recent Analyses</span>
              </h3>
              <Link
                to="/history"
                className="text-xs font-semibold text-emerald-700 hover:text-emerald-900"
              >
                History
              </Link>
            </div>

            <div className="divide-y divide-gray-100 text-xs">
              {foodHistory.slice(0, 3).map((item) => (
                <div key={item.id} className="py-2.5 flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">{item.food_name}</p>
                    <p className="text-[11px] text-gray-400">
                      {item.serving_size_g}g • {Math.round(item.calories)} kcal
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate("/scanner")}
                  >
                    View
                  </Button>
                </div>
              ))}
              {foodHistory.length === 0 && (
                <p className="text-xs text-gray-400 py-3 text-center">
                  No activity recorded yet.
                </p>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
