import React, { useState, useEffect } from "react";
import {
  ChefHat,
  Sparkles,
  Clock,
  Users,
  CheckSquare,
  Square,
  Bookmark,
  BookmarkCheck,
  Send,
  Search,
  Trash2,
  AlertCircle,
  HelpCircle,
  ChevronRight,
  Flame,
} from "lucide-react";
import { Button } from "../../components/common/Button";
import { Card } from "../../components/common/Card";
import { Badge } from "../../components/common/Badge";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { api } from "../../api/client";
import { Recipe, RecipeIngredient } from "../../types";
import { useAuth } from "../../context/AuthContext";

export const CookingPage: React.FC = () => {
  const { isAuthenticated, openAuthModal } = useAuth();

  // Generator inputs
  const [dishQuery, setDishQuery] = useState("");
  const [ingredientsInput, setIngredientsInput] = useState("");
  const [cuisine, setCuisine] = useState("Indian");
  const [servings, setServings] = useState(2);
  const [cookingTime, setCookingTime] = useState(30);
  const [restrictions, setRestrictions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Active Recipe State
  const [activeRecipe, setActiveRecipe] = useState<Recipe | null>(null);
  const [ingredientChecklist, setIngredientChecklist] = useState<Record<number, boolean>>({});
  const [isSaved, setIsSaved] = useState(false);

  // Conversational Assistant
  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [chatLoading, setChatLoading] = useState(false);

  // Saved Recipes Library
  const [savedRecipes, setSavedRecipes] = useState<Recipe[]>([]);
  const [searchSaved, setSearchSaved] = useState("");

  const cuisines = [
    "Indian",
    "Mediterranean",
    "Asian / Stir-Fry",
    "Italian",
    "Mexican",
    "Global Healthy",
  ];

  const commonRestrictions = ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Low-Carb"];

  useEffect(() => {
    if (isAuthenticated) {
      loadSavedRecipes();
    }
  }, [isAuthenticated]);

  const loadSavedRecipes = async () => {
    try {
      const data = await api.getSavedRecipes();
      setSavedRecipes(data);
    } catch {
      // Ignored
    }
  };

  const handleGenerateRecipe = async () => {
    setLoading(true);
    setError(null);
    setIsSaved(false);
    setChatHistory([]);

    const ingredientsList = ingredientsInput
      .split(",")
      .map((i) => i.trim())
      .filter(Boolean);

    try {
      const recipe = await api.generateRecipe({
        query: dishQuery || "Balanced Nutritious Meal",
        ingredients: ingredientsList,
        dietary_restrictions: restrictions,
        cuisine,
        servings,
        cooking_time_min: cookingTime,
      });

      setActiveRecipe(recipe);
      setIngredientChecklist({});
    } catch (err: any) {
      setError(err.message || "Failed to generate recipe.");
    } finally {
      setLoading(false);
    }
  };

  const toggleIngredientCheck = (idx: number) => {
    setIngredientChecklist((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const handleSaveRecipe = async () => {
    if (!isAuthenticated) {
      openAuthModal("login");
      return;
    }
    if (!activeRecipe) return;

    try {
      const saved = await api.saveRecipe(activeRecipe);
      setIsSaved(true);
      setSavedRecipes([saved, ...savedRecipes]);
    } catch (err: any) {
      setError(err.message || "Failed to save recipe.");
    }
  };

  const handleDeleteSaved = async (id?: string) => {
    if (!id) return;
    try {
      await api.deleteRecipe(id);
      setSavedRecipes(savedRecipes.filter((r) => r.id !== id));
      if (activeRecipe?.id === id) {
        setIsSaved(false);
      }
    } catch {
      // Ignored
    }
  };

  const handleSendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;

    const userMsg = chatMessage.trim();
    setChatMessage("");
    setChatHistory((prev) => [...prev, { role: "user", content: userMsg }]);
    setChatLoading(true);

    try {
      const res = await api.chatRecipe({
        message: userMsg,
        current_recipe: activeRecipe,
        conversation_history: chatHistory,
      });

      setChatHistory((prev) => [...prev, { role: "assistant", content: res.reply }]);
    } catch {
      setChatHistory((prev) => [
        ...prev,
        { role: "assistant", content: "Apologies, could not process that request right now." },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const toggleRestriction = (r: string) => {
    if (restrictions.includes(r)) {
      setRestrictions(restrictions.filter((x) => x !== r));
    } else {
      setRestrictions([...restrictions, r]);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">
          <ChefHat className="w-4 h-4" />
          <span>Interactive Culinary Assistant</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
          Smart Cooking Assistant & Recipe Builder
        </h1>
        <p className="text-xs sm:text-sm text-gray-500 mt-1 max-w-2xl">
          Enter available ingredients, target cooking times, or regional cravings.
          Get step-by-step guidance with allergen substitutions, gram measurements, and conversational adjustments.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Generator Form (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <Card className="p-6 space-y-4">
            <h2 className="text-sm font-bold text-gray-900 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-600" />
              <span>Recipe Generator</span>
            </h2>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                What would you like to cook?
              </label>
              <input
                type="text"
                placeholder="e.g. High-protein paneer curry, Dal khichdi, Lentil stew"
                value={dishQuery}
                onChange={(e) => setDishQuery(e.target.value)}
                className="w-full text-xs rounded-xl border border-gray-200 p-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                Available Ingredients (Comma separated)
              </label>
              <textarea
                rows={2}
                placeholder="e.g. Paneer, bell peppers, tomatoes, ginger, cumin, olive oil"
                value={ingredientsInput}
                onChange={(e) => setIngredientsInput(e.target.value)}
                className="w-full text-xs rounded-xl border border-gray-200 p-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Cuisine
                </label>
                <select
                  value={cuisine}
                  onChange={(e) => setCuisine(e.target.value)}
                  className="w-full text-xs rounded-xl border border-gray-200 p-2 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  {cuisines.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Servings
                </label>
                <select
                  value={servings}
                  onChange={(e) => setServings(Number(e.target.value))}
                  className="w-full text-xs rounded-xl border border-gray-200 p-2 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  {[1, 2, 4, 6, 8].map((s) => (
                    <option key={s} value={s}>
                      {s} {s === 1 ? "Person" : "People"}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                Dietary Restrictions
              </label>
              <div className="flex flex-wrap gap-1.5">
                {commonRestrictions.map((r) => (
                  <button
                    type="button"
                    key={r}
                    onClick={() => toggleRestriction(r)}
                    className={`px-2.5 py-1 text-xs rounded-lg border transition-colors ${
                      restrictions.includes(r)
                        ? "bg-emerald-700 text-white border-emerald-700 font-semibold"
                        : "bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100"
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>

            <Button
              variant="primary"
              size="md"
              className="w-full mt-2"
              onClick={handleGenerateRecipe}
              loading={loading}
              icon={<Sparkles className="w-4 h-4" />}
            >
              Generate Precision Recipe
            </Button>

            {error && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{error}</span>
              </div>
            )}
          </Card>

          {/* Saved Recipes Library */}
          <Card className="p-6">
            <h2 className="text-sm font-bold text-gray-900 mb-2 flex items-center justify-between">
              <span>Saved Recipes Library</span>
              <Badge variant="neutral" size="sm">
                {savedRecipes.length}
              </Badge>
            </h2>

            {savedRecipes.length > 0 && (
              <div className="relative mb-3">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Filter saved recipes..."
                  value={searchSaved}
                  onChange={(e) => setSearchSaved(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 text-xs rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            )}

            <div className="max-h-60 overflow-y-auto space-y-2">
              {savedRecipes
                .filter((r) => r.title.toLowerCase().includes(searchSaved.toLowerCase()))
                .map((r) => (
                  <div
                    key={r.id}
                    className="p-2.5 rounded-xl border border-gray-100 hover:border-emerald-200 hover:bg-emerald-50/40 flex items-center justify-between transition-colors text-xs"
                  >
                    <div>
                      <p className="font-semibold text-gray-900">{r.title}</p>
                      <p className="text-[11px] text-gray-400">
                        {r.cuisine} • {r.prep_time_min + r.cook_time_min} mins
                      </p>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setActiveRecipe(r);
                          setIsSaved(true);
                        }}
                      >
                        Open
                      </Button>
                      <button
                        onClick={() => handleDeleteSaved(r.id)}
                        className="text-gray-400 hover:text-rose-600 p-1 rounded-lg"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              {savedRecipes.length === 0 && (
                <p className="text-xs text-gray-400 py-3 text-center">
                  No saved recipes yet. Generate and click "Save Recipe".
                </p>
              )}
            </div>
          </Card>
        </div>

        {/* Right Column: Recipe Details & Conversational Follow-up (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {loading ? (
            <Card className="p-12">
              <LoadingSpinner
                message="Crafting personalized recipe with exact gram measurements and allergen substitutions..."
                size="lg"
              />
            </Card>
          ) : activeRecipe ? (
            <div className="space-y-6">
              <Card className="p-6 space-y-6">
                {/* Recipe Header */}
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-4 border-b border-gray-100">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Badge variant="success" size="sm">
                        {activeRecipe.cuisine}
                      </Badge>
                      <Badge variant="neutral" size="sm">
                        {activeRecipe.difficulty}
                      </Badge>
                    </div>
                    <h2 className="text-xl font-extrabold text-gray-900">
                      {activeRecipe.title}
                    </h2>
                    {activeRecipe.description && (
                      <p className="text-xs text-gray-600 leading-relaxed">
                        {activeRecipe.description}
                      </p>
                    )}
                  </div>

                  <Button
                    variant={isSaved ? "secondary" : "outline"}
                    size="sm"
                    onClick={handleSaveRecipe}
                    icon={
                      isSaved ? (
                        <BookmarkCheck className="w-4 h-4 text-emerald-700" />
                      ) : (
                        <Bookmark className="w-4 h-4" />
                      )
                    }
                  >
                    {isSaved ? "Saved" : "Save Recipe"}
                  </Button>
                </div>

                {/* Quick Stats Bar */}
                <div className="grid grid-cols-3 gap-3 p-3 rounded-xl bg-gray-50 border border-gray-100 text-center text-xs">
                  <div>
                    <span className="text-[11px] text-gray-400 block font-medium">Prep Time</span>
                    <span className="font-bold text-gray-800 flex items-center justify-center gap-1 mt-0.5">
                      <Clock className="w-3.5 h-3.5 text-emerald-600" />
                      {activeRecipe.prep_time_min} mins
                    </span>
                  </div>
                  <div>
                    <span className="text-[11px] text-gray-400 block font-medium">Cook Time</span>
                    <span className="font-bold text-gray-800 flex items-center justify-center gap-1 mt-0.5">
                      <Flame className="w-3.5 h-3.5 text-amber-600" />
                      {activeRecipe.cook_time_min} mins
                    </span>
                  </div>
                  <div>
                    <span className="text-[11px] text-gray-400 block font-medium">Portions</span>
                    <span className="font-bold text-gray-800 flex items-center justify-center gap-1 mt-0.5">
                      <Users className="w-3.5 h-3.5 text-blue-600" />
                      {activeRecipe.servings} Servings
                    </span>
                  </div>
                </div>

                {/* Ingredients Checklist */}
                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider flex items-center justify-between">
                    <span>Interactive Ingredient Checklist</span>
                    <span className="text-[11px] text-emerald-700 font-semibold lowercase">
                      click to cross off
                    </span>
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {activeRecipe.ingredients.map((ing, idx) => {
                      const isChecked = ingredientChecklist[idx] || false;
                      return (
                        <div
                          key={idx}
                          onClick={() => toggleIngredientCheck(idx)}
                          className={`p-2.5 rounded-xl border text-xs flex items-center gap-2.5 cursor-pointer transition-colors ${
                            isChecked
                              ? "bg-emerald-50/60 border-emerald-200 text-gray-400 line-through"
                              : "bg-white border-gray-100 hover:border-gray-200 text-gray-800"
                          }`}
                        >
                          {isChecked ? (
                            <CheckSquare className="w-4 h-4 text-emerald-600 shrink-0" />
                          ) : (
                            <Square className="w-4 h-4 text-gray-300 shrink-0" />
                          )}
                          <div className="flex-1 flex items-center justify-between">
                            <span className="font-semibold">{ing.item}</span>
                            <span className="text-gray-500 font-medium">{ing.quantity}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Instructions */}
                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                    Step-by-Step Cooking Method
                  </h3>
                  <div className="space-y-2.5">
                    {activeRecipe.instructions.map((step, idx) => (
                      <div
                        key={idx}
                        className="flex items-start gap-3 p-3 rounded-xl bg-gray-50/70 border border-gray-100 text-xs text-gray-800 leading-relaxed"
                      >
                        <span className="w-5 h-5 rounded-md bg-emerald-700 text-white font-bold flex items-center justify-center shrink-0 text-[10px]">
                          {idx + 1}
                        </span>
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Substitutions & Food Safety */}
                {activeRecipe.substitutions?.length > 0 && (
                  <div className="space-y-2">
                    <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                      Smart Ingredient Substitutions
                    </h3>
                    <div className="space-y-1.5">
                      {activeRecipe.substitutions.map((sub, idx) => (
                        <div
                          key={idx}
                          className="p-2.5 rounded-xl bg-amber-50/60 border border-amber-100 text-xs text-amber-950 flex items-start gap-2"
                        >
                          <ChevronRight className="w-3.5 h-3.5 text-amber-700 shrink-0 mt-0.5" />
                          <span>
                            <strong>Replace {sub.original}:</strong> Use {sub.alternative} ({sub.reason})
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeRecipe.food_safety_notes && (
                  <div className="p-3 rounded-xl bg-gray-50 border border-gray-100 text-[11px] text-gray-600">
                    <strong>Food Safety & Storage:</strong> {activeRecipe.food_safety_notes}
                  </div>
                )}
              </Card>

              {/* Conversational Follow-up Assistant */}
              <Card className="p-6 space-y-4">
                <div className="flex items-center gap-2">
                  <ChefHat className="w-4 h-4 text-emerald-700" />
                  <h3 className="text-sm font-bold text-gray-900">
                    Ask Follow-up Questions About This Recipe
                  </h3>
                </div>

                <div className="space-y-2.5 max-h-56 overflow-y-auto">
                  {chatHistory.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-xl text-xs leading-relaxed ${
                        msg.role === "user"
                          ? "bg-emerald-700 text-white ml-6"
                          : "bg-gray-50 text-gray-800 border border-gray-100 mr-6"
                      }`}
                    >
                      {msg.content}
                    </div>
                  ))}
                  {chatLoading && (
                    <div className="p-3 rounded-xl bg-gray-50 border border-gray-100 text-xs text-gray-500 animate-pulse mr-6">
                      Chef AI is tailoring recipe adjustments...
                    </div>
                  )}
                </div>

                <form onSubmit={handleSendChat} className="flex gap-2">
                  <input
                    type="text"
                    placeholder="e.g. How can I boost protein? Or what if I don't have cumin?"
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    className="flex-1 text-xs rounded-xl border border-gray-200 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                  <Button
                    type="submit"
                    variant="primary"
                    size="md"
                    loading={chatLoading}
                    icon={<Send className="w-3.5 h-3.5" />}
                  >
                    Ask
                  </Button>
                </form>
              </Card>
            </div>
          ) : (
            <Card className="p-12 text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-orange-50 border border-orange-100 flex items-center justify-center mx-auto text-orange-700">
                <ChefHat className="w-8 h-8" />
              </div>
              <div className="max-w-md mx-auto">
                <h3 className="text-base font-bold text-gray-900">
                  Ready to Create Recipes
                </h3>
                <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">
                  Enter your ingredients or dish request on the left. You'll receive step-by-step methods, ingredient checklists, and live culinary follow-ups.
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
