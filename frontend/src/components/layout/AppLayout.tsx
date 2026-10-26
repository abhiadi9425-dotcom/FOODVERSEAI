import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import { Navbar } from "../common/Navbar";
import { Sidebar } from "../common/Sidebar";
import { Footer } from "../common/Footer";
import { AuthModal } from "../../features/auth/AuthModal";

export const AppLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#FAFAF8] flex flex-col font-sans">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex flex-1">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          <div className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
            <Outlet />
          </div>
          <Footer />
        </main>
      </div>
      <AuthModal />
    </div>
  );
};
