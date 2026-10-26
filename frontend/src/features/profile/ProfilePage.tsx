import React, { useState, useEffect } from "react";
import {
  User,
  Settings,
  Heart,
  ShieldAlert,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Cpu,
  Save,
  Plus,
} from "lucide-react";
import { Button } from "../../components/common/Button";
import { Card } from "../../components/common/Card";
import { Badge } from "../../components/common/Badge";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { api } from "../../api/client";
import { UserProfile, ProviderStatus } from "../../types";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";

export const ProfilePage: React.FC = () => {
  const { user, profile, refreshProfile, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [providerStatus, setProviderStatus] = useState<ProviderStatus | null>(null);

  // Form State
  const [age, setAge] = useState<number | "">(profile?.age || "");
  const [height, setHeight] = useState<number | "">(profile?.height_cm || "");
  const [weight, setWeight] = useState<number | "">(profile?.weight_kg || "");
  const [activityLevel, setActivityLevel] = useState<string>(profile?.activity_level || "moderate");
  const [dietaryPattern, setDietaryPattern] = useState<string>(profile?.dietary_pattern || "omnivore");
  const [goal, setGoal] = useState<string>(profile?.goal || "maintenance");
  const [allergies, setAllergies] = useState<string[]>(profile?.allergies || []);
  const [allergyInput, setAllergyInput] = useState("");
  const [cuisines, setCuisines] = useState<string[]>(profile?.cuisine_preferences || ["Indian", "Global"]);

  useEffect(() => {
    if (profile) {
      setAge(profile.age || "");
      setHeight(profile.height_cm || "");
      setWeight(profile.weight_kg || "");
      setActivityLevel(profile.activity_level || "moderate");
      setDietaryPattern(profile.dietary_pattern || "omnivore");
      setGoal(profile.goal || "maintenance");
      setAllergies(profile.allergies || []);
      setCuisines(profile.cuisine_preferences || ["Indian", "Global"]);
    }
  }, [profile]);

  useEffect(() => {
    api.getHealth().then((res) => setProviderStatus(res.ai_providers)).catch(() => null);
  }, []);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await api.updateProfile({
        age: age ? Number(age) : undefined,
        height_cm: height ? Number(height) : undefined,
        weight_kg: weight ? Number(weight) : undefined,
        activity_level: activityLevel,
        dietary_pattern: dietaryPattern,
        goal,
        allergies,
        cuisine_preferences: cuisines,
      });

      await refreshProfile();
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to update profile.");
    } finally {
      setLoading(false);
    }
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

  const handleDeleteAccount = async () => {
    if (
      window.confirm(
        "Are you absolutely sure you want to permanently delete your account? All food scans, recipes, and meal plans will be wiped."
      )
    ) {
      try {
        await api.deleteAccount();
        logout();
        navigate("/");
      } catch (err: any) {
        setError(err.message || "Could not delete account.");
      }
    }
  };

  if (!isAuthenticated) {
    return (
      <Card className="p-12 text-center space-y-4">
        <h2 className="text-lg font-bold text-gray-900">Sign in Required</h2>
        <p className="text-xs text-gray-500">
          Please sign in or create an account to configure your health metrics and dietary goals.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">
          <Settings className="w-4 h-4" />
          <span>Account & Dietary Profiles</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
          Profile & Nutritional Settings
        </h1>
        <p className="text-xs sm:text-sm text-gray-500 mt-1">
          Configure your physiological targets, dietary restrictions, and AI provider integrations.
        </p>
      </div>

      {success && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Profile and dietary restrictions updated successfully!</span>
        </div>
      )}

      {error && (
        <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSaveProfile} className="space-y-6">
        {/* Account Info */}
        <Card className="p-6 space-y-4">
          <h2 className="text-sm font-bold text-gray-900 border-b border-gray-100 pb-2 flex items-center gap-2">
            <User className="w-4 h-4 text-emerald-700" />
            <span>Account Details</span>
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-gray-500 font-semibold mb-1">Full Name</label>
              <input
                type="text"
                disabled
                value={user?.full_name || ""}
                className="w-full text-xs rounded-xl border border-gray-200 p-2.5 bg-gray-50 text-gray-600 cursor-not-allowed"
              />
            </div>
            <div>
              <label className="block text-gray-500 font-semibold mb-1">Email Address</label>
              <input
                type="email"
                disabled
                value={user?.email || ""}
                className="w-full text-xs rounded-xl border border-gray-200 p-2.5 bg-gray-50 text-gray-600 cursor-not-allowed"
              />
            </div>
          </div>
        </Card>

        {/* Health Metrics & Target Goals */}
        <Card className="p-6 space-y-4">
          <h2 className="text-sm font-bold text-gray-900 border-b border-gray-100 pb-2 flex items-center gap-2">
            <Heart className="w-4 h-4 text-rose-600" />
            <span>Physiological Metrics & Targets</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-gray-700 font-semibold mb-1">Age (Years)</label>
              <input
                type="number"
                min="10"
                max="120"
                placeholder="e.g. 28"
                value={age}
                onChange={(e) => setAge(e.target.value === "" ? "" : Number(e.target.value))}
                className="w-full text-xs rounded-xl border border-gray-200 p-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-1">Height (cm)</label>
              <input
                type="number"
                min="50"
                max="250"
                placeholder="e.g. 175"
                value={height}
                onChange={(e) => setHeight(e.target.value === "" ? "" : Number(e.target.value))}
                className="w-full text-xs rounded-xl border border-gray-200 p-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-1">Weight (kg)</label>
              <input
                type="number"
                min="20"
                max="300"
                placeholder="e.g. 70"
                value={weight}
                onChange={(e) => setWeight(e.target.value === "" ? "" : Number(e.target.value))}
                className="w-full text-xs rounded-xl border border-gray-200 p-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs pt-2">
            <div>
              <label className="block text-gray-700 font-semibold mb-1">Activity Level</label>
              <select
                value={activityLevel}
                onChange={(e) => setActivityLevel(e.target.value)}
                className="w-full text-xs rounded-xl border border-gray-200 p-2.5 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="sedentary">Sedentary (Little or no exercise)</option>
                <option value="light">Lightly Active (1-3 days/week)</option>
                <option value="moderate">Moderately Active (3-5 days/week)</option>
                <option value="active">Very Active (6-7 days/week)</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-1">Primary Dietary Goal</label>
              <select
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                className="w-full text-xs rounded-xl border border-gray-200 p-2.5 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="healthy_eating">General Healthy Eating & Vitality</option>
                <option value="muscle_gain">Muscle Synthesis & High Protein</option>
                <option value="weight_loss">Calorie Deficit / Fat Loss</option>
                <option value="maintenance">Maintenance</option>
                <option value="diabetic_friendly">Diabetic Friendly / Glycemic Control</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Dietary Patterns & Allergies */}
        <Card className="p-6 space-y-4">
          <h2 className="text-sm font-bold text-gray-900 border-b border-gray-100 pb-2 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-700" />
            <span>Dietary Pattern & Allergens</span>
          </h2>

          <div className="text-xs">
            <label className="block text-gray-700 font-semibold mb-1">Dietary Pattern</label>
            <select
              value={dietaryPattern}
              onChange={(e) => setDietaryPattern(e.target.value)}
              className="w-full text-xs rounded-xl border border-gray-200 p-2.5 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="omnivore">Omnivore (Standard Balanced)</option>
              <option value="vegetarian">Vegetarian (Lacto-Ovo)</option>
              <option value="vegan">Vegan (100% Plant-Based)</option>
              <option value="pescatarian">Pescatarian</option>
              <option value="sattvic">Sattvic (Ayurvedic Pure Vegetarian)</option>
              <option value="keto">Keto (High Fat, Low Carb)</option>
            </select>
          </div>

          <div className="text-xs">
            <label className="block text-gray-700 font-semibold mb-1 flex items-center justify-between">
              <span>Strict Allergen Exclusions (Zero Tolerance)</span>
              <span className="text-[11px] text-gray-400">Meal planner filters these 100%</span>
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                placeholder="e.g. Peanuts, Dairy, Shellfish, Gluten"
                value={allergyInput}
                onChange={(e) => setAllergyInput(e.target.value)}
                className="flex-1 text-xs rounded-xl border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
              <Button type="button" variant="secondary" size="sm" onClick={addAllergy}>
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {allergies.map((a) => (
                <span
                  key={a}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs bg-rose-50 border border-rose-200 text-rose-900 font-semibold"
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
            </div>
          </div>
        </Card>

        {/* AI Model & Data Source Status */}
        <Card className="p-6 space-y-4">
          <h2 className="text-sm font-bold text-gray-900 border-b border-gray-100 pb-2 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-emerald-700" />
            <span>AI Model & Data Source Integrations</span>
          </h2>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-gray-50 border border-gray-100">
              <div>
                <p className="font-semibold text-gray-900">Active Reasoning Engine</p>
                <p className="text-[11px] text-gray-500">
                  {providerStatus?.active_provider === "groq"
                    ? "Groq Cloud (qwen/qwen3.8-27b & whisper-large-v3-turbo)"
                    : providerStatus?.active_provider === "gemini"
                    ? "Google Gemini 2.5 Flash (Configured)"
                    : providerStatus?.active_provider === "openai"
                    ? "OpenAI GPT-4o (Configured)"
                    : "Verified Reference Database Engine (No External API Key Needed)"}
                </p>
              </div>
              <Badge variant="success" size="sm">
                Connected
              </Badge>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-gray-50 border border-gray-100">
              <div>
                <p className="font-semibold text-gray-900">Nutrition Composition Database</p>
                <p className="text-[11px] text-gray-500">
                  {providerStatus?.verified_reference_db || "USDA FoodData Central"}
                </p>
              </div>
              <Badge variant="success" size="sm">
                Verified
              </Badge>
            </div>
          </div>
        </Card>

        <div className="flex items-center justify-between pt-2">
          <Button
            type="submit"
            variant="primary"
            size="md"
            loading={loading}
            icon={<Save className="w-4 h-4" />}
          >
            Save All Preferences
          </Button>

          <Button
            type="button"
            variant="danger"
            size="sm"
            onClick={handleDeleteAccount}
            icon={<Trash2 className="w-4 h-4" />}
          >
            Delete Account & Wipe Data
          </Button>
        </div>
      </form>
    </div>
  );
};
