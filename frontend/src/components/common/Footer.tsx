import React from "react";
import { ShieldCheck, HeartHandshake } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-gray-100 bg-white py-8 px-4 sm:px-8 mt-auto text-xs text-gray-500">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-md bg-emerald-700 flex items-center justify-center text-white text-[10px] font-bold">
            F
          </div>
          <span className="font-semibold text-gray-800">FoodVerse AI</span>
          <span>— Multimodal Food Intelligence</span>
        </div>

        <div className="flex items-center gap-6 text-[11px] text-gray-500">
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            Verified USDA & ICMR Reference Data
          </span>
          <span className="flex items-center gap-1.5">
            <HeartHandshake className="w-3.5 h-3.5 text-emerald-600" />
            Zero-Tolerance Allergen Safety
          </span>
        </div>

        <div className="text-[11px] text-gray-400">
          © {new Date().getFullYear()} FoodVerse AI. Built for precision nutrition and kitchen intelligence.
        </div>
      </div>
    </footer>
  );
};
