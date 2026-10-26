import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Sparkles,
  User as UserIcon,
  LogOut,
  Menu,
  X,
  ShieldCheck,
  ChevronDown,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { Button } from "./Button";
import { api } from "../../api/client";
import { ProviderStatus } from "../../types";

interface NavbarProps {
  onToggleSidebar?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  const { user, isAuthenticated, logout, openAuthModal } = useAuth();
  const navigate = useNavigate();
  const [providerStatus, setProviderStatus] = useState<ProviderStatus | null>(null);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  useEffect(() => {
    api
      .getHealth()
      .then((res) => setProviderStatus(res.ai_providers))
      .catch(() => null);
  }, []);

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/90 backdrop-blur-md border-b border-gray-100 flex items-center justify-between px-4 sm:px-6">
      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="p-2 -ml-2 text-gray-600 hover:text-gray-900 lg:hidden rounded-lg hover:bg-gray-100"
            aria-label="Toggle menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-800 to-emerald-600 flex items-center justify-center text-white shadow-sm group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <span className="text-lg font-bold text-gray-900 tracking-tight flex items-center gap-1.5">
              FoodVerse <span className="text-emerald-700 text-xs px-1.5 py-0.5 bg-emerald-50 border border-emerald-200 rounded-md font-semibold">AI</span>
            </span>
          </div>
        </Link>
      </div>

      {/* AI Provider Status Pill & Actions */}
      <div className="flex items-center gap-3">
        {providerStatus && (
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50/80 border border-emerald-200 text-emerald-800">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>
              {providerStatus.active_provider === "groq"
                ? "Groq Ultra-Fast AI Active"
                : providerStatus.active_provider === "gemini"
                ? "Gemini Multimodal Active"
                : providerStatus.active_provider === "openai"
                ? "OpenAI GPT-4o Active"
                : "USDA Verified DB Active"}
            </span>
          </div>
        )}

        {isAuthenticated ? (
          <div className="relative">
            <button
              onClick={() => setUserDropdownOpen(!userDropdownOpen)}
              className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-gray-100 transition-colors"
            >
              <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs">
                {user?.full_name?.charAt(0) || user?.email.charAt(0).toUpperCase()}
              </div>
              <span className="text-xs font-semibold text-gray-700 hidden sm:inline-block max-w-[120px] truncate">
                {user?.full_name || user?.email.split("@")[0]}
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
            </button>

            {userDropdownOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setUserDropdownOpen(false)}
                />
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-elevated border border-gray-100 py-1.5 z-20 animate-in fade-in zoom-in-95 duration-100">
                  <div className="px-3.5 py-2 border-b border-gray-100">
                    <p className="text-xs font-semibold text-gray-900 truncate">
                      {user?.full_name || "FoodVerse User"}
                    </p>
                    <p className="text-[11px] text-gray-500 truncate">{user?.email}</p>
                  </div>
                  <button
                    onClick={() => {
                      setUserDropdownOpen(false);
                      navigate("/profile");
                    }}
                    className="w-full flex items-center gap-2 px-3.5 py-2 text-xs text-gray-700 hover:bg-emerald-50 hover:text-emerald-800 transition-colors"
                  >
                    <UserIcon className="w-4 h-4" />
                    <span>Profile & Preferences</span>
                  </button>
                  <button
                    onClick={() => {
                      setUserDropdownOpen(false);
                      logout();
                      navigate("/");
                    }}
                    className="w-full flex items-center gap-2 px-3.5 py-2 text-xs text-rose-600 hover:bg-rose-50 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => openAuthModal("login")}
            >
              Sign In
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => openAuthModal("register")}
            >
              Get Started
            </Button>
          </div>
        )}
      </div>
    </header>
  );
};
