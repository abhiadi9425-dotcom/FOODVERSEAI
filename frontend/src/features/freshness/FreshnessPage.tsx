import React, { useState, useEffect, useRef } from "react";
import {
  Apple,
  Upload,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ShieldAlert,
  Info,
  Clock,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import { Button } from "../../components/common/Button";
import { Card } from "../../components/common/Card";
import { Badge } from "../../components/common/Badge";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { api } from "../../api/client";
import { FreshnessAssessment } from "../../types";
import { useAuth } from "../../context/AuthContext";

export const FreshnessPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [category, setCategory] = useState<string>("Fresh Produce / Fruits");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FreshnessAssessment | null>(null);
  const [history, setHistory] = useState<FreshnessAssessment[]>([]);

  const foodCategories = [
    "Fresh Produce / Fruits",
    "Vegetables & Leafy Greens",
    "Poultry & Raw Meats",
    "Seafood & Fresh Fish",
    "Dairy & Cheese",
    "Bakery & Breads",
    "Cooked Leftovers",
  ];

  useEffect(() => {
    if (isAuthenticated) {
      api.getFreshnessHistory().then(setHistory).catch(() => null);
    }
  }, [isAuthenticated]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError("Please select or drop an image of the food item to inspect.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("image", selectedFile);
      formData.append("food_category", category);

      const assessment = await api.analyzeFreshness(formData);
      setResult(assessment);

      if (isAuthenticated) {
        api.getFreshnessHistory().then(setHistory).catch(() => null);
      }
    } catch (err: any) {
      setError(err.message || "Failed to analyze freshness. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (categoryStr: string) => {
    if (categoryStr.includes("No obvious")) {
      return (
        <Badge variant="success" size="md" className="gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          No Obvious Visual Spoilage
        </Badge>
      );
    } else if (categoryStr.includes("Visible quality")) {
      return (
        <Badge variant="warning" size="md" className="gap-1.5">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
          Visible Quality Concerns
        </Badge>
      );
    } else {
      return (
        <Badge variant="danger" size="md" className="gap-1.5">
          <XCircle className="w-3.5 h-3.5 text-rose-600" />
          Potential Spoilage Indicators
        </Badge>
      );
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">
          <Apple className="w-4 h-4" />
          <span>Surface Quality & Spoilage Auditing</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
          Food Freshness & Spoilage Assessment
        </h1>
        <p className="text-xs sm:text-sm text-gray-500 mt-1 max-w-2xl">
          Examine visible signs of discoloration, mold-like mycelium, wilting, and surface degradation.
          Always prioritize certified public health guidelines over photograph appearance.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Input Form (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <Card className="p-6">
            <h2 className="text-sm font-bold text-gray-900 mb-4">
              Select Food Item for Inspection
            </h2>

            {/* Category Selector */}
            <div className="mb-4">
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                Food Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full text-xs rounded-xl border border-gray-200 p-2.5 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                {foodCategories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            {/* Dropzone */}
            {!previewUrl ? (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-gray-200 hover:border-emerald-500 rounded-2xl p-8 text-center cursor-pointer bg-gray-50/50 hover:bg-emerald-50/20 transition-all group"
              >
                <div className="w-12 h-12 rounded-xl bg-white shadow-sm border border-gray-200 flex items-center justify-center mx-auto mb-3 text-emerald-700 group-hover:scale-105 transition-transform">
                  <Upload className="w-6 h-6" />
                </div>
                <p className="text-xs font-bold text-gray-900">
                  Click or drag photo of food item
                </p>
                <p className="text-[11px] text-gray-400 mt-1">
                  Focus closely on surface spots, edges, or packaging
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
                    alt="Food item"
                    className="max-h-full max-w-full object-contain"
                  />
                  <button
                    onClick={() => {
                      setSelectedFile(null);
                      setPreviewUrl(null);
                    }}
                    className="absolute top-2 right-2 bg-black/60 text-white rounded-lg p-1.5 hover:bg-black/80"
                  >
                    Change Photo
                  </button>
                </div>
                <Button
                  variant="primary"
                  size="md"
                  className="w-full"
                  onClick={handleAnalyze}
                  loading={loading}
                  icon={<Apple className="w-4 h-4" />}
                >
                  Run Freshness Assessment
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

          {/* Critical Food Safety Notice Box */}
          <Card className="p-5 bg-gradient-to-br from-amber-50 to-orange-50/40 border-amber-200">
            <div className="flex items-start gap-2.5">
              <ShieldAlert className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h3 className="text-xs font-bold text-amber-900 uppercase tracking-wider">
                  Important Public Health Guidance
                </h3>
                <p className="text-[11px] text-amber-800 leading-relaxed">
                  Bacterial pathogens (such as Salmonella, Listeria, and Staphylococcus) produce dangerous foodborne toxins without creating visible surface discoloration or odor. If an item has exceeded safe refrigeration durations, discard it immediately regardless of appearance.
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Column: Assessment Result (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {loading ? (
            <Card className="p-12">
              <LoadingSpinner
                message="Inspecting surface discoloration, bruising, and fungal morphology..."
                size="lg"
              />
            </Card>
          ) : result ? (
            <div className="space-y-6">
              <Card className="p-6 space-y-6">
                {/* Result header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-100">
                  <div>
                    <span className="text-xs text-gray-400 uppercase font-semibold block mb-1">
                      Visual Assessment Category
                    </span>
                    {getStatusBadge(result.assessment_category)}
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-gray-500 block">Food Category</span>
                    <span className="text-sm font-bold text-gray-900">
                      {result.food_category}
                    </span>
                  </div>
                </div>

                {/* Visual Observations Checklist */}
                <div className="space-y-2">
                  <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                    Visible Surface Observations
                  </h3>
                  <div className="space-y-2">
                    {result.visual_observations.map((obs, idx) => (
                      <div
                        key={idx}
                        className="flex items-start gap-2.5 p-3 rounded-xl bg-gray-50 text-xs text-gray-700 border border-gray-100"
                      >
                        <ChevronRight className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                        <span>{obs}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Practical Recommendations */}
                <div className="space-y-2">
                  <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Recommended Next Steps
                  </h3>
                  <div className="space-y-2">
                    {result.recommendations.map((rec, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-emerald-50/60 border border-emerald-100 text-xs text-emerald-950 font-medium"
                      >
                        {rec}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Safety Disclaimer Banner */}
                <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-950 text-xs space-y-1">
                  <span className="font-bold flex items-center gap-1.5 text-rose-900">
                    <ShieldAlert className="w-4 h-4 text-rose-700" /> Food Safety Disclaimer
                  </span>
                  <p className="leading-relaxed text-[11px] text-rose-900">
                    {result.safety_disclaimer}
                  </p>
                </div>
              </Card>
            </div>
          ) : (
            <Card className="p-12 text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-amber-50 border border-amber-100 flex items-center justify-center mx-auto text-amber-700">
                <Apple className="w-8 h-8" />
              </div>
              <div className="max-w-md mx-auto">
                <h3 className="text-base font-bold text-gray-900">
                  No Food Selected for Inspection
                </h3>
                <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">
                  Upload an image of produce, dairy, or meats on the left. The system will inspect observable discoloration, spots, and surface texture.
                </p>
              </div>
            </Card>
          )}

          {/* Past Freshness Checks */}
          {isAuthenticated && history.length > 0 && (
            <Card className="p-6">
              <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center justify-between">
                <span>Recent Freshness Checks</span>
                <span className="text-xs text-gray-400">{history.length} records</span>
              </h3>
              <div className="divide-y divide-gray-100">
                {history.slice(0, 5).map((item, idx) => (
                  <div
                    key={item.id || idx}
                    className="py-3 flex items-center justify-between gap-4 text-xs"
                  >
                    <div>
                      <p className="font-semibold text-gray-900">{item.food_category}</p>
                      <p className="text-[11px] text-gray-400">
                        {item.assessment_category}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setResult(item)}
                    >
                      View Report
                    </Button>
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
