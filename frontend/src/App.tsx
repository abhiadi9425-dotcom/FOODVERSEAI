import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { AppLayout } from "./components/layout/AppLayout";
import { LandingPage } from "./features/landing/LandingPage";
import { DashboardPage } from "./features/dashboard/DashboardPage";
import { FoodScannerPage } from "./features/scanner/FoodScannerPage";
import { FreshnessPage } from "./features/freshness/FreshnessPage";
import { HygienePage } from "./features/hygiene/HygienePage";
import { CookingPage } from "./features/cooking/CookingPage";
import { MealPlannerPage } from "./features/meal-planner/MealPlannerPage";
import { AssistantPage } from "./features/assistant/AssistantPage";
import { HistoryPage } from "./features/history/HistoryPage";
import { ProfilePage } from "./features/profile/ProfilePage";

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading, openAuthModal } = useAuth();

  if (loading) {
    return null;
  }

  if (!isAuthenticated) {
    return <LandingPage />;
  }

  return <>{children}</>;
};

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<LandingPage />} />
            <Route
              path="dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route path="scanner" element={<FoodScannerPage />} />
            <Route path="freshness" element={<FreshnessPage />} />
            <Route path="hygiene" element={<HygienePage />} />
            <Route path="cooking" element={<CookingPage />} />
            <Route path="meal-planner" element={<MealPlannerPage />} />
            <Route path="assistant" element={<AssistantPage />} />
            <Route path="history" element={<HistoryPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
