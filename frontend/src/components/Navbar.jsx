import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import {
  Brain,
  LayoutDashboard,
  FileText,
  MessageSquare,
  Award,
  Calendar,
  Sparkles,
  BarChart3,
  LogOut,
  User,
  Activity,
  Menu,
  X,
} from "lucide-react";

export const Navbar = ({ activeTab, setActiveTab }) => {
  const { user, logout } = useAuth();
  const [healthStatus, setHealthStatus] = useState("checking");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        const res = await api.health.check();
        setHealthStatus(res.data.status === "healthy" ? "healthy" : "degraded");
      } catch (err) {
        setHealthStatus("disconnected");
      }
    };
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "documents", label: "Documents", icon: FileText },
    { id: "chat", label: "AI Study Assistant", icon: MessageSquare },
    { id: "quiz", label: "Quizzes", icon: Award },
    { id: "studyplan", label: "Study Plan", icon: Calendar },
    { id: "classifier", label: "Topic Classifier", icon: Sparkles },
    { id: "analytics", label: "Progress", icon: BarChart3 },
  ];

  return (
    <header className="glass-panel sticky top-0 z-50 px-4 lg:px-8 py-3 mb-6 mx-2 sm:mx-6 mt-3 border border-white/10">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo */}
        <div
          onClick={() => setActiveTab("dashboard")}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/30 group-hover:scale-105 transition-transform">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-xl tracking-tight text-white font-['Outfit']">
                StudyMate<span className="text-indigo-400">.AI</span>
              </span>
              <span className="badge badge-indigo text-[10px] py-0.5 px-2">v1.0</span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Adaptive AI Study Assistant
            </p>
          </div>
        </div>

        {/* Desktop Navigation Links */}
        <nav className="hidden lg:flex items-center gap-1 bg-slate-900/60 p-1.5 rounded-xl border border-white/5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                    : "text-slate-300 hover:text-white hover:bg-white/5"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Section: System Health + User Menu */}
        <div className="hidden sm:flex items-center gap-3">
          {/* Health indicator */}
          <div
            title={`Backend Status: ${healthStatus}`}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/60 border border-white/5 text-xs text-slate-300"
          >
            <span
              className={`w-2 h-2 rounded-full ${
                healthStatus === "healthy"
                  ? "bg-emerald-400 shadow-[0_0_8px_#34d399]"
                  : healthStatus === "checking"
                  ? "bg-amber-400 animate-pulse"
                  : "bg-rose-500 shadow-[0_0_8px_#f43f5e]"
              }`}
            />
            <span className="text-[11px] font-medium capitalize">
              {healthStatus === "healthy" ? "API Live" : healthStatus}
            </span>
          </div>

          {/* User profile & Logout */}
          <div className="flex items-center gap-2 pl-2 border-l border-white/10">
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-white/5 border border-white/5">
              <div className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-300 flex items-center justify-center text-xs font-semibold">
                {user?.username?.charAt(0).toUpperCase() || "U"}
              </div>
              <span className="text-sm font-medium text-slate-200 max-w-[100px] truncate">
                {user?.username || "Student"}
              </span>
            </div>

            <button
              onClick={logout}
              title="Sign Out"
              className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Mobile Menu Hamburger */}
        <div className="lg:hidden flex items-center gap-2">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg bg-white/5 border border-white/10 text-slate-300"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden mt-4 pt-4 border-t border-white/10 flex flex-col gap-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-indigo-600 text-white"
                    : "text-slate-300 hover:bg-white/5"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}

          <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-between px-2">
            <span className="text-sm text-slate-300">Signed in as {user?.username}</span>
            <button
              onClick={logout}
              className="btn btn-danger text-xs py-1.5 px-3"
            >
              <LogOut className="w-3.5 h-3.5" /> Sign Out
            </button>
          </div>
        </div>
      )}
    </header>
  );
};
