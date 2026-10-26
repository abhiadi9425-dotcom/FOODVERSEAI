import React from "react";
import { useNavigate } from "react-router-dom";
import {
  ScanLine,
  Apple,
  Video,
  ChefHat,
  CalendarDays,
  BotMessageSquare,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Database,
  Cpu,
  Eye,
  Lock,
} from "lucide-react";
import { Button } from "../../components/common/Button";
import { Card } from "../../components/common/Card";
import { useAuth } from "../../context/AuthContext";

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, openAuthModal } = useAuth();

  const handleStart = () => {
    if (isAuthenticated) {
      navigate("/dashboard");
    } else {
      openAuthModal("register");
    }
  };

  const capabilities = [
    {
      title: "Food Recognition & Nutrition",
      description:
        "Upload food images to identify dishes and calculate verified calories, macronutrients, and micronutrients scaled precisely to gram portions from USDA FoodData Central.",
      icon: ScanLine,
      color: "bg-emerald-50 text-emerald-700 border-emerald-200",
      route: "/scanner",
    },
    {
      title: "Freshness & Spoilage Check",
      description:
        "Evidence-based visual inspection of produce, dairy, and meats. Evaluates discoloration, texture, and mold-like patterns with authoritative food-safety guidance.",
      icon: Apple,
      color: "bg-amber-50 text-amber-700 border-amber-200",
      route: "/freshness",
    },
    {
      title: "Kitchen Hygiene Video Monitoring",
      description:
        "Upload commercial kitchen footage. Uses OpenCV keyframe extraction and vision AI to evaluate glove usage, hair restraints, and cross-contamination risks.",
      icon: Video,
      color: "bg-blue-50 text-blue-700 border-blue-200",
      route: "/hygiene",
    },
    {
      title: "Smart Cooking Assistant",
      description:
        "Interactive culinary guidance accepting available ingredients, preparation time, and cuisine preferences. Features step-by-step instructions and ingredient checklists.",
      icon: ChefHat,
      color: "bg-orange-50 text-orange-700 border-orange-200",
      route: "/cooking",
    },
    {
      title: "Personalized Meal Planning",
      description:
        "Generate daily and weekly plans tailored to fitness goals, dietary patterns, and strict zero-tolerance allergen exclusions with derived nutrition calculations.",
      icon: CalendarDays,
      color: "bg-purple-50 text-purple-700 border-purple-200",
      route: "/meal-planner",
    },
    {
      title: "Multimodal AI Assistant",
      description:
        "Central voice and text assistant. Routes queries across nutrition, culinary science, freshness concerns, and grocery planning with full user profile context.",
      icon: BotMessageSquare,
      color: "bg-teal-50 text-teal-700 border-teal-200",
      route: "/assistant",
    },
  ];

  return (
    <div className="space-y-16 pb-12">
      {/* Hero Section */}
      <section className="relative pt-6 sm:pt-12 text-center max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Multimodal Intelligence & Verified USDA Composition Pipeline</span>
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-gray-900 tracking-tight leading-[1.15]">
          Intelligent Nutrition, Culinary & Kitchen Analysis
        </h1>

        <p className="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
          FoodVerse AI connects computer vision, speech transcription, large language models,
          and laboratory nutrition data into a unified, science-backed platform for home cooks,
          athletes, and commercial kitchens.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <Button
            size="lg"
            variant="primary"
            onClick={handleStart}
            icon={<ArrowRight className="w-5 h-5" />}
          >
            Start Analyzing Food
          </Button>
          <Button
            size="lg"
            variant="outline"
            onClick={() => navigate("/scanner")}
          >
            Explore Food Scanner
          </Button>
        </div>
      </section>

      {/* Six Capabilities Grid */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight">
            Six Modular Intelligence Capabilities
          </h2>
          <p className="text-xs sm:text-sm text-gray-500 mt-2">
            Engineered with clear separation of concerns, verified data sources, and truthful AI boundaries.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {capabilities.map((cap) => {
            const Icon = cap.icon;
            return (
              <Card
                key={cap.title}
                hover
                onClick={() => navigate(cap.route)}
                className="p-6 flex flex-col justify-between"
              >
                <div className="space-y-4">
                  <div
                    className={`w-12 h-12 rounded-xl border flex items-center justify-center ${cap.color}`}
                  >
                    <Icon className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-gray-900">{cap.title}</h3>
                    <p className="text-xs text-gray-600 mt-1.5 leading-relaxed">
                      {cap.description}
                    </p>
                  </div>
                </div>
                <div className="pt-4 mt-4 border-t border-gray-100 flex items-center text-xs font-semibold text-emerald-700">
                  <span>Launch Capability</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1.5 group-hover:translate-x-1 transition-transform" />
                </div>
              </Card>
            );
          })}
        </div>
      </section>

      {/* How the System Works */}
      <section className="bg-white rounded-3xl p-8 sm:p-12 border border-gray-100/90 shadow-card space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight">
            How the Multimodal Pipeline Operates
          </h2>
          <p className="text-xs sm:text-sm text-gray-500">
            A deterministic, auditable pipeline combining genuine computer vision with verified nutrition science.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 flex items-center justify-center font-bold text-sm">
              01
            </div>
            <h3 className="text-sm font-bold text-gray-900 flex items-center gap-1.5">
              <Eye className="w-4 h-4 text-emerald-600" />
              Multimodal Ingestion
            </h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Accepts high-resolution images, MP4/MOV videos, audio recordings, or text descriptions with server-side MIME type verification and path-traversal safeguards.
            </p>
          </div>

          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 flex items-center justify-center font-bold text-sm">
              02
            </div>
            <h3 className="text-sm font-bold text-gray-900 flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-emerald-600" />
              Neural & Verified Analysis
            </h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Routes visual features through configured vision models (Gemini / OpenAI), extracts OpenCV video keyframes, and maps identified dishes to USDA FoodData Central tables.
            </p>
          </div>

          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 flex items-center justify-center font-bold text-sm">
              03
            </div>
            <h3 className="text-sm font-bold text-gray-900 flex items-center gap-1.5">
              <Database className="w-4 h-4 text-emerald-600" />
              Truthful Scaled Intelligence
            </h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Delivers exact portion scaling in grams, derives meal macronutrient sums from constituent ingredients, enforces strict allergen exclusions, and records private history.
            </p>
          </div>
        </div>
      </section>

      {/* Privacy and Responsible AI Directive */}
      <section className="bg-gradient-to-br from-emerald-900 to-emerald-950 text-white rounded-3xl p-8 sm:p-12 shadow-elevated space-y-6">
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-800/60 border border-emerald-700/50 text-emerald-200 text-xs font-semibold">
            <Lock className="w-3.5 h-3.5" />
            <span>Responsible AI & Data Privacy Architecture</span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
            Scientific Truthfulness & Safety Boundaries
          </h2>

          <div className="space-y-3 text-xs sm:text-sm text-emerald-100/90 leading-relaxed">
            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong>No Microbiological Safety Guarantees:</strong> Visual inspection cannot detect colorless, odorless pathogens such as Salmonella, Listeria, or toxins. FoodVerse AI always advises following official public health storage and temperature standards.
              </span>
            </div>
            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong>Transparent Calorie Estimation:</strong> Nutritional calculations distinguish deterministic USDA reference values from single-photo portion approximations. Users can freely correct detected dish names and gram weights.
              </span>
            </div>
            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong>Private Data Isolation:</strong> Every scan, recipe, and meal plan is strictly bound to the authenticated user ID with complete account deletion controls. API credentials remain private on the backend.
              </span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
