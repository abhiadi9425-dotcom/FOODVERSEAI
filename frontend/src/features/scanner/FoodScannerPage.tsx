import React, { useState, useEffect, useRef } from "react";
import {
  Upload,
  ScanLine,
  Image as ImageIcon,
  X,
  RefreshCw,
  Info,
  CheckCircle2,
  Trash2,
  Scale,
  Search,
  Sparkles,
} from "lucide-react";
import { Button } from "../../components/common/Button";
import { Card } from "../../components/common/Card";
import { Badge } from "../../components/common/Badge";
import { NutritionChart } from "../../components/common/NutritionChart";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { api } from "../../api/client";
import { FoodAnalysis, VerifiedDatabaseItem } from "../../types";
import { useAuth } from "../../context/AuthContext";

export const FoodScannerPage: React.FC = () => {
  const { isAuthenticated, openAuthModal } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<FoodAnalysis | null>(null);
  const [servingGrams, setServingGrams] = useState<number>(100);
  const [dbItems, setDbItems] = useState<VerifiedDatabaseItem[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [history, setHistory] = useState<FoodAnalysis[]>([]);

  useEffect(() => {
    // Load verified database items
    api.getVerifiedDatabaseItems().then(setDbItems).catch(() => null);

    // Load user's recent history if authenticated
    if (isAuthenticated) {
      loadHistory();
    }
  }, [isAuthenticated]);

  const loadHistory = async () => {
    try {
      const data = await api.getFoodHistory();
      setHistory(data);
    } catch {
      // Ignored
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleAnalyze = async (foodNameOverride?: string) => {
    if (!selectedFile && !foodNameOverride) {
      setError("Please select an image to scan or choose a dish from the verified database.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      if (selectedFile) {
        formData.append("image", selectedFile);
      }
      if (foodNameOverride) {
        formData.append("food_name", foodNameOverride);
      }
      formData.append("serving_size_g", servingGrams.toString());

      const result = await api.analyzeFood(formData);
      setAnalysisResult(result);
      setServingGrams(result.serving_size_g);

      if (isAuthenticated) {
        loadHistory();
      }
    } catch (err: any) {
      setError(err.message || "Failed to analyze food. Please check your image or network.");
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculateServing = async (newGrams: number) => {
    setServingGrams(newGrams);
    if (!analysisResult) return;

    try {
      const updated = await api.recalculateNutrition(analysisResult.food_name, newGrams);
      setAnalysisResult({
        ...analysisResult,
        ...updated,
        serving_size_g: newGrams,
      });
    } catch {
      // Keep previous
    }
  };

  const handleDeleteHistory = async (id: string) => {
    try {
      await api.deleteFoodAnalysis(id);
      setHistory(history.filter((h) => h.id !== id));
      if (analysisResult?.id === id) {
        setAnalysisResult(null);
      }
    } catch {
      // Ignored
    }
  };

  const filteredItems = dbItems.filter(
    (item) =>
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">
          <ScanLine className="w-4 h-4" />
          <span>Multimodal Vision & USDA Composition</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
          Food Scanner & Nutrition Analysis
        </h1>
        <p className="text-xs sm:text-sm text-gray-500 mt-1">
          Upload any food photo to detect dish components, scale portions in grams, and calculate verified USDA laboratory nutrition.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Upload & Quick Select (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <Card className="p-6">
            <h2 className="text-sm font-bold text-gray-900 mb-4 flex items-center justify-between">
              <span>Upload Food Image</span>
              {previewUrl && (
                <button
                  onClick={clearSelection}
                  className="text-xs text-rose-600 hover:text-rose-800 flex items-center gap-1"
                >
                  <X className="w-3.5 h-3.5" /> Remove
                </button>
              )}
            </h2>

            {/* Dropzone */}
            {!previewUrl ? (
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-gray-200 hover:border-emerald-500 rounded-2xl p-8 text-center cursor-pointer bg-gray-50/50 hover:bg-emerald-50/20 transition-all group"
              >
                <div className="w-12 h-12 rounded-xl bg-white shadow-sm border border-gray-200 flex items-center justify-center mx-auto mb-3 text-emerald-700 group-hover:scale-105 transition-transform">
                  <Upload className="w-6 h-6" />
                </div>
                <p className="text-xs font-bold text-gray-900">
                  Click to select or drag and drop image
                </p>
                <p className="text-[11px] text-gray-400 mt-1">
                  Supports JPG, PNG, WEBP (Max 15 MB)
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp,image/jpg"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative rounded-2xl overflow-hidden border border-gray-200 bg-black aspect-video max-h-64 flex items-center justify-center">
                  <img
                    src={previewUrl}
                    alt="Food preview"
                    className="max-h-full max-w-full object-contain"
                  />
                </div>
                <Button
                  variant="primary"
                  size="md"
                  className="w-full"
                  onClick={() => handleAnalyze()}
                  loading={loading}
                  icon={<ScanLine className="w-4 h-4" />}
                >
                  Analyze Uploaded Image
                </Button>
              </div>
            )}

            {error && (
              <div className="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2">
                <Info className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{error}</span>
              </div>
            )}
          </Card>

          {/* Quick Select from Verified Database */}
          <Card className="p-6">
            <h2 className="text-sm font-bold text-gray-900 mb-2 flex items-center justify-between">
              <span>Verified Food Reference Database</span>
              <Badge variant="success" size="sm">
                USDA & ICMR Lab
              </Badge>
            </h2>
            <p className="text-xs text-gray-500 mb-3">
              Directly select or search verified dishes without needing a camera.
            </p>

            <div className="relative mb-3">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search Vegetable Poha, Dal Tadka, Salmon, Roti..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div className="max-h-56 overflow-y-auto space-y-1.5 pr-1">
              {filteredItems.slice(0, 10).map((item) => (
                <button
                  key={item.key}
                  onClick={() => {
                    setServingGrams(item.default_serving_g);
                    handleAnalyze(item.name);
                  }}
                  className="w-full text-left p-2.5 rounded-xl hover:bg-emerald-50 border border-gray-100 hover:border-emerald-200 flex items-center justify-between transition-colors text-xs group"
                >
                  <div>
                    <p className="font-semibold text-gray-900 group-hover:text-emerald-950">
                      {item.name}
                    </p>
                    <p className="text-[11px] text-gray-400">
                      {item.serving_description} • {item.calories_per_100g} kcal/100g
                    </p>
                  </div>
                  <Badge variant="neutral" size="sm">
                    Select
                  </Badge>
                </button>
              ))}
            </div>
          </Card>
        </div>

        {/* Right Column: Nutrition Results & Charts (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {loading ? (
            <Card className="p-12">
              <LoadingSpinner
                message="Running neural food identification and scaling USDA laboratory nutrients..."
                size="lg"
              />
            </Card>
          ) : analysisResult ? (
            <div className="space-y-6">
              {/* Primary Dish Card */}
              <Card className="p-6">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-4 border-b border-gray-100">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h2 className="text-xl font-extrabold text-gray-900">
                        {analysisResult.food_name}
                      </h2>
                      {analysisResult.confidence && (
                        <Badge variant="success" size="sm">
                          {Math.round(analysisResult.confidence * 100)}% Confidence
                        </Badge>
                      )}
                    </div>
                    {analysisResult.alternate_names?.length > 0 && (
                      <p className="text-xs text-gray-500">
                        Also known as: {analysisResult.alternate_names.join(", ")}
                      </p>
                    )}
                  </div>

                  <div className="text-right">
                    <span className="text-3xl font-black text-emerald-800">
                      {Math.round(analysisResult.calories)}
                    </span>
                    <span className="text-xs text-gray-500 uppercase block font-semibold">
                      Total Calories (kcal)
                    </span>
                  </div>
                </div>

                {/* Interactive Serving Adjuster */}
                <div className="py-4 border-b border-gray-100 space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-gray-700">
                    <span className="flex items-center gap-1.5">
                      <Scale className="w-3.5 h-3.5 text-emerald-600" />
                      Adjust Portion Weight:
                    </span>
                    <span className="font-bold text-emerald-800 text-sm">
                      {servingGrams} g
                    </span>
                  </div>
                  <input
                    type="range"
                    min="25"
                    max="1000"
                    step="25"
                    value={servingGrams}
                    onChange={(e) => handleRecalculateServing(Number(e.target.value))}
                    className="w-full accent-emerald-600 cursor-pointer"
                  />
                  <div className="flex items-center justify-between text-[11px] text-gray-400">
                    <span>Small snack (50g)</span>
                    <span>Standard meal (250g)</span>
                    <span>Large bowl (500g+)</span>
                  </div>
                </div>

                {/* Donut Chart & Grams */}
                <div className="pt-4">
                  <NutritionChart
                    protein_g={analysisResult.protein_g}
                    carbs_g={analysisResult.carbs_g}
                    fat_g={analysisResult.fat_g}
                    calories={analysisResult.calories}
                  />
                </div>

                {/* Nutrient Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-4 border-t border-gray-100">
                  <div className="p-3 rounded-xl bg-gray-50 text-center">
                    <span className="text-[11px] font-semibold text-gray-500 uppercase block">
                      Dietary Fiber
                    </span>
                    <span className="text-base font-bold text-gray-900">
                      {analysisResult.fiber_g} g
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-gray-50 text-center">
                    <span className="text-[11px] font-semibold text-gray-500 uppercase block">
                      Sugars
                    </span>
                    <span className="text-base font-bold text-gray-900">
                      {analysisResult.sugar_g} g
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-gray-50 text-center">
                    <span className="text-[11px] font-semibold text-gray-500 uppercase block">
                      Sodium
                    </span>
                    <span className="text-base font-bold text-gray-900">
                      {analysisResult.sodium_mg} mg
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-gray-50 text-center">
                    <span className="text-[11px] font-semibold text-gray-500 uppercase block">
                      Data Type
                    </span>
                    <span className="text-xs font-bold text-emerald-800">
                      {analysisResult.is_estimate ? "Approximation" : "Verified Reference"}
                    </span>
                  </div>
                </div>

                {/* Micronutrients if available */}
                {Object.keys(analysisResult.micronutrients || {}).length > 0 && (
                  <div className="mt-4 p-3 rounded-xl bg-emerald-50/60 border border-emerald-100 text-xs text-emerald-950 space-y-1">
                    <span className="font-bold flex items-center gap-1 text-emerald-900">
                      <Sparkles className="w-3.5 h-3.5" /> Key Micronutrients & Minerals:
                    </span>
                    <div className="flex flex-wrap gap-2 pt-1 text-[11px]">
                      {Object.entries(analysisResult.micronutrients).map(([k, v]) => (
                        <span key={k} className="px-2 py-0.5 rounded-md bg-white border border-emerald-200 font-medium">
                          {k.replace("_", " ").toUpperCase()}: {v}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Provenance and Disclaimer Note */}
                <div className="mt-4 p-3 rounded-xl bg-gray-50 border border-gray-100 text-[11px] text-gray-500 space-y-1">
                  <p>
                    <strong>Source Provenance:</strong> {analysisResult.data_source}
                  </p>
                  {analysisResult.notes && (
                    <p className="text-gray-600">{analysisResult.notes}</p>
                  )}
                </div>
              </Card>
            </div>
          ) : (
            /* Empty State */
            <Card className="p-12 text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center mx-auto text-emerald-700">
                <ImageIcon className="w-8 h-8" />
              </div>
              <div className="max-w-md mx-auto">
                <h3 className="text-base font-bold text-gray-900">
                  Ready for Food Ingestion
                </h3>
                <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">
                  Upload an image on the left or select a verified dish from the database to see an interactive macronutrient donut chart, calorie breakdowns, and portion scalers.
                </p>
              </div>
            </Card>
          )}

          {/* User's Recent Food Analysis History */}
          {isAuthenticated && history.length > 0 && (
            <Card className="p-6">
              <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center justify-between">
                <span>Recent Analyses (Private to You)</span>
                <span className="text-xs text-gray-400">{history.length} records</span>
              </h3>
              <div className="divide-y divide-gray-100">
                {history.slice(0, 5).map((item) => (
                  <div
                    key={item.id}
                    className="py-3 flex items-center justify-between gap-4 text-xs"
                  >
                    <div>
                      <p className="font-semibold text-gray-900">{item.food_name}</p>
                      <p className="text-[11px] text-gray-400">
                        {item.serving_size_g}g • {Math.round(item.calories)} kcal • P: {item.protein_g}g | C: {item.carbs_g}g | F: {item.fat_g}g
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setAnalysisResult(item);
                          setServingGrams(item.serving_size_g);
                        }}
                      >
                        View
                      </Button>
                      <button
                        onClick={() => item.id && handleDeleteHistory(item.id)}
                        className="text-gray-400 hover:text-rose-600 p-1 rounded-lg"
                        title="Delete record"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
