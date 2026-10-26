import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

interface NutritionChartProps {
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  calories: number;
}

export const NutritionChart: React.FC<NutritionChartProps> = ({
  protein_g,
  carbs_g,
  fat_g,
  calories,
}) => {
  const proteinCals = protein_g * 4;
  const carbsCals = carbs_g * 4;
  const fatCals = fat_g * 9;
  const totalMacroCals = proteinCals + carbsCals + fatCals || 1;

  const data = [
    {
      name: "Protein",
      value: Math.round(proteinCals),
      grams: protein_g,
      pct: Math.round((proteinCals / totalMacroCals) * 100),
      color: "#059669", // emerald-600
    },
    {
      name: "Carbohydrates",
      value: Math.round(carbsCals),
      grams: carbs_g,
      pct: Math.round((carbsCals / totalMacroCals) * 100),
      color: "#d97706", // amber-600
    },
    {
      name: "Fats",
      value: Math.round(fatCals),
      grams: fat_g,
      pct: Math.round((fatCals / totalMacroCals) * 100),
      color: "#ea580c", // orange-600
    },
  ];

  return (
    <div className="flex flex-col sm:flex-row items-center gap-6">
      {/* Donut Chart */}
      <div className="relative w-44 h-44 shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              innerRadius={52}
              outerRadius={70}
              paddingAngle={4}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} strokeWidth={0} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: any, name: any) => [`${value} kcal`, name]}
              contentStyle={{
                backgroundColor: "#ffffff",
                borderRadius: "12px",
                border: "1px solid #e5e7eb",
                boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
                fontSize: "12px",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-bold text-gray-900 tracking-tight">
            {Math.round(calories)}
          </span>
          <span className="text-xs uppercase font-medium text-gray-400">kcal</span>
        </div>
      </div>

      {/* Legend & Gram Breakdowns */}
      <div className="grid grid-cols-3 sm:grid-cols-1 gap-3 w-full">
        {data.map((item) => (
          <div
            key={item.name}
            className="flex flex-col sm:flex-row sm:items-center justify-between p-2.5 rounded-xl bg-gray-50/80 border border-gray-100"
          >
            <div className="flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 rounded-full shrink-0"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-xs font-semibold text-gray-700">{item.name}</span>
            </div>
            <div className="flex items-center gap-2 mt-1 sm:mt-0 text-xs">
              <span className="font-bold text-gray-900">{item.grams}g</span>
              <span className="text-gray-400">({item.pct}%)</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
