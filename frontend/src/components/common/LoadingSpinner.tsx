import React from "react";
import { Loader2 } from "lucide-react";

interface LoadingSpinnerProps {
  message?: string;
  size?: "sm" | "md" | "lg";
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = "Processing with FoodVerse AI...",
  size = "md",
}) => {
  const iconSizes = {
    sm: "w-5 h-5",
    md: "w-8 h-8",
    lg: "w-12 h-12",
  };

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 space-y-3">
      <div className="relative">
        <Loader2 className={`${iconSizes[size]} text-emerald-600 animate-spin`} />
        <div className="absolute inset-0 rounded-full border-2 border-emerald-100 opacity-20 animate-ping" />
      </div>
      {message && <p className="text-sm font-medium text-gray-600 animate-pulse">{message}</p>}
    </div>
  );
};
