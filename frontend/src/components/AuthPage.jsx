import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Brain, Lock, Mail, User, ArrowRight, Sparkles, CheckCircle2, AlertCircle } from "lucide-react";

export const AuthPage = () => {
  const { login, register, authError, setAuthError } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    if (authError) setAuthError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    if (isRegister) {
      if (!form.username || !form.email || !form.password) {
        setAuthError("All fields are required.");
        setLoading(false);
        return;
      }
      await register(form.username, form.email, form.password);
    } else {
      if (!form.username || !form.password) {
        setAuthError("Please provide your username and password.");
        setLoading(false);
        return;
      }
      await login(form.username, form.password);
    }
    setLoading(false);
  };

  const fillDemoAccount = () => {
    setForm({
      username: "alex_student",
      email: "alex@studymate.ai",
      password: "StudyPass123!",
    });
  };

  return (
    <div className="aurora-bg min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-500 items-center justify-center shadow-xl shadow-indigo-500/30 mb-4 animate-bounce-subtle">
            <Brain className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-3xl font-extrabold text-white font-['Outfit'] tracking-tight">
            StudyMate<span className="text-indigo-400">.AI</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1.5">
            Your Adaptive AI Study Assistant & RAG Knowledge Partner
          </p>
        </div>

        {/* Auth Glass Card */}
        <div className="glass-panel p-8 relative overflow-hidden">
          {/* Subtle top glow bar */}
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-violet-500 to-cyan-500" />

          {/* Tab Switcher */}
          <div className="flex bg-slate-900/80 p-1 rounded-xl mb-6 border border-white/5">
            <button
              type="button"
              onClick={() => {
                setIsRegister(false);
                setAuthError(null);
              }}
              className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${
                !isRegister
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setIsRegister(true);
                setAuthError(null);
              }}
              className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${
                isRegister
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Register
            </button>
          </div>

          {/* Error Alert */}
          {authError && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 flex items-start gap-2.5 text-rose-300 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{authError}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                Username
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  name="username"
                  value={form.username}
                  onChange={handleChange}
                  placeholder="e.g. alex_student"
                  className="input-field pl-10"
                  autoComplete="username"
                  required
                />
              </div>
            </div>

            {isRegister && (
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                  <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="student@university.edu"
                    className="input-field pl-10"
                    autoComplete="email"
                    required
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="password"
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="••••••••••••"
                  className="input-field pl-10"
                  autoComplete="current-password"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full py-3 mt-2 text-base font-semibold"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Processing...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2">
                  <span>{isRegister ? "Create Account" : "Sign In to StudyMate"}</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              )}
            </button>
          </form>

          {/* Quick Demo Fill Button */}
          <div className="mt-6 pt-5 border-t border-white/10 text-center">
            <button
              type="button"
              onClick={fillDemoAccount}
              className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Fill sample student credentials</span>
            </button>
          </div>
        </div>

        {/* Feature Highlights Footer */}
        <div className="mt-8 grid grid-cols-3 gap-3 text-center text-[11px] text-slate-400">
          <div className="flex flex-col items-center gap-1 p-2 rounded-lg bg-white/[0.02]">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>PDF/TXT RAG</span>
          </div>
          <div className="flex flex-col items-center gap-1 p-2 rounded-lg bg-white/[0.02]">
            <CheckCircle2 className="w-4 h-4 text-indigo-400" />
            <span>AI Practice Quiz</span>
          </div>
          <div className="flex flex-col items-center gap-1 p-2 rounded-lg bg-white/[0.02]">
            <CheckCircle2 className="w-4 h-4 text-violet-400" />
            <span>Adaptive Plans</span>
          </div>
        </div>
      </div>
    </div>
  );
};
