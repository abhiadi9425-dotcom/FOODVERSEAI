import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  ScanLine,
  Apple,
  Video,
  ChefHat,
  CalendarDays,
  BotMessageSquare,
  History,
  Settings,
  X,
  Sparkles,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { isAuthenticated } = useAuth();

  const navItems = [
    { name: "Overview", path: "/dashboard", icon: LayoutDashboard },
    { name: "Food Scanner", path: "/scanner", icon: ScanLine },
    { name: "Freshness Checker", path: "/freshness", icon: Apple },
    { name: "Kitchen Hygiene", path: "/hygiene", icon: Video },
    { name: "Cooking Assistant", path: "/cooking", icon: ChefHat },
    { name: "Meal Planner", path: "/meal-planner", icon: CalendarDays },
    { name: "Multimodal Assistant", path: "/assistant", icon: BotMessageSquare },
    { name: "History & Logs", path: "/history", icon: History },
    { name: "Profile & Settings", path: "/profile", icon: Settings },
  ];

  const content = (
    <div className="flex flex-col h-full bg-white border-r border-gray-100/90 w-64">
      {/* Brand & Mobile Close */}
      <div className="h-16 px-5 flex items-center justify-between border-b border-gray-100 lg:hidden">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-700 flex items-center justify-center text-white">
            <Sparkles className="w-4 h-4" />
          </div>
          <span className="font-bold text-gray-900">FoodVerse AI</span>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Nav items */}
      <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-gray-400 uppercase">
          Intelligence Capabilities
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 ${
                  isActive
                    ? "bg-emerald-700 text-white shadow-sm font-bold"
                    : "text-gray-600 hover:text-emerald-900 hover:bg-emerald-50/70"
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </div>

      {/* Bottom Info card */}
      <div className="p-4 m-3 rounded-2xl bg-gradient-to-br from-emerald-50 to-emerald-100/40 border border-emerald-100">
        <div className="flex items-center gap-2 text-emerald-900 text-xs font-bold mb-1">
          <Sparkles className="w-3.5 h-3.5 text-emerald-700" />
          <span>Multimodal Agent</span>
        </div>
        <p className="text-[11px] text-emerald-800 leading-relaxed">
          USDA composition data with vision and speech intelligence.
        </p>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside className="hidden lg:block shrink-0 sticky top-16 h-[calc(100vh-4rem)]">
        {content}
      </aside>

      {/* Mobile Slide-out Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm transition-opacity"
            onClick={onClose}
          />
          <div className="fixed inset-y-0 left-0 w-64 z-50 transform transition-transform duration-200 ease-in-out">
            {content}
          </div>
        </div>
      )}
    </>
  );
};
