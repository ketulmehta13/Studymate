import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import {
  FileText,
  Award,
  Calendar,
  MessageSquare,
  Sparkles,
  ArrowRight,
  TrendingUp,
  CheckCircle,
  Clock,
  BookOpen,
  Plus,
  RefreshCw,
} from "lucide-react";

export const Dashboard = ({ setActiveTab }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    metrics: {
      documents_uploaded: 0,
      quizzes_completed: 0,
      average_quiz_score: 0,
      questions_asked: 0,
      completed_tasks: 0,
    },
    topic_mastery: {},
    recent_documents: [],
    recent_quizzes: [],
    active_study_plan: null,
  });

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const res = await api.progress.getSummary();
      setData(res.data);
    } catch (err) {
      console.error("Failed to load dashboard metrics", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      {/* Welcome Banner */}
      <div className="glass-panel p-6 sm:p-8 relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-6 border border-indigo-500/20">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI-Driven Adaptive Learning</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            {getGreeting()},{" "}
            <span className="gradient-text">{user?.username || "Student"}</span>!
          </h1>
          <p className="text-slate-300 mt-2 text-sm sm:text-base leading-relaxed">
            Ready to master your coursework? Ask questions against your uploaded study notes,
            generate practice quizzes, and track your personalized study plan.
          </p>
        </div>

        <div className="relative z-10 flex flex-wrap gap-3">
          <button
            onClick={() => setActiveTab("chat")}
            className="btn btn-primary"
          >
            <MessageSquare className="w-4 h-4" />
            <span>Ask AI Assistant</span>
          </button>
          <button
            onClick={() => setActiveTab("documents")}
            className="btn btn-secondary"
          >
            <Plus className="w-4 h-4" />
            <span>Upload Notes</span>
          </button>
        </div>

        {/* Ambient background decoration */}
        <div className="absolute -right-10 -bottom-10 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="glass-panel glass-panel-hover p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Study Notes
            </span>
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl sm:text-3xl font-extrabold text-white">
              {data.metrics.documents_uploaded}
            </div>
            <p className="text-xs text-slate-400 mt-1">PDF & TXT indexed</p>
          </div>
        </div>

        {/* Metric 2 */}
        <div className="glass-panel glass-panel-hover p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Quizzes Taken
            </span>
            <div className="p-2 rounded-xl bg-violet-500/10 text-violet-400 border border-violet-500/20">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl sm:text-3xl font-extrabold text-white">
              {data.metrics.quizzes_completed}
            </div>
            <p className="text-xs text-slate-400 mt-1">Practice sessions</p>
          </div>
        </div>

        {/* Metric 3 */}
        <div className="glass-panel glass-panel-hover p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Average Score
            </span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl sm:text-3xl font-extrabold text-white">
              {data.metrics.average_quiz_score}%
            </div>
            <p className="text-xs text-slate-400 mt-1">Knowledge retention</p>
          </div>
        </div>

        {/* Metric 4 */}
        <div className="glass-panel glass-panel-hover p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Tasks Done
            </span>
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <CheckCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl sm:text-3xl font-extrabold text-white">
              {data.metrics.completed_tasks}
            </div>
            <p className="text-xs text-slate-400 mt-1">From active plan</p>
          </div>
        </div>
      </div>

      {/* Main Grid: Topic Mastery & Active Study Plan */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Topic Mastery Overview */}
        <div className="glass-panel p-6 lg:col-span-1 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-indigo-400" />
                <span>Topic Mastery</span>
              </h2>
              <button
                onClick={() => setActiveTab("quiz")}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
              >
                Take Quiz →
              </button>
            </div>
            <p className="text-xs text-slate-400 mb-6">
              Calculated from your practice quiz submissions across academic subjects.
            </p>

            <div className="space-y-4">
              {Object.keys(data.topic_mastery).length > 0 ? (
                Object.entries(data.topic_mastery).map(([topic, pct]) => (
                  <div key={topic} className="space-y-1.5">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-slate-300">{topic}</span>
                      <span
                        className={
                          pct >= 75
                            ? "text-emerald-400"
                            : pct >= 50
                            ? "text-amber-400"
                            : "text-rose-400"
                        }
                      >
                        {pct}%
                      </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          pct >= 75
                            ? "bg-gradient-to-r from-emerald-500 to-teal-400"
                            : pct >= 50
                            ? "bg-gradient-to-r from-amber-500 to-yellow-400"
                            : "bg-gradient-to-r from-rose-500 to-pink-500"
                        }`}
                        style={{ width: `${Math.min(100, Math.max(5, pct))}%` }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-slate-400 text-sm">
                  <Award className="w-10 h-10 text-slate-600 mx-auto mb-2" />
                  <p>No quiz results yet.</p>
                  <button
                    onClick={() => setActiveTab("quiz")}
                    className="btn btn-primary text-xs mt-3 py-1.5 px-3"
                  >
                    Generate your first quiz
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-white/5">
            <button
              onClick={() => setActiveTab("classifier")}
              className="w-full flex items-center justify-between text-xs text-slate-400 hover:text-white transition-colors"
            >
              <span className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                Analyze syllabus with ML classifier
              </span>
              <span>→</span>
            </button>
          </div>
        </div>

        {/* Right Column: Active Study Plan & Recent Activity */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Plan Widget */}
          <div className="glass-panel p-6 border border-white/10">
            <div className="flex items-center justify-between mb-4">
              <div>
                <span className="badge badge-indigo text-[10px] mb-1">
                  Active Schedule
                </span>
                <h2 className="text-xl font-bold text-white">
                  {data.active_study_plan?.title || "Adaptive Weekly Study Plan"}
                </h2>
              </div>
              <button
                onClick={() => setActiveTab("studyplan")}
                className="btn btn-secondary text-xs py-1.5 px-3"
              >
                View Full Plan
              </button>
            </div>

            {data.active_study_plan ? (
              <div className="space-y-4">
                <div className="flex items-center gap-4 text-xs text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-indigo-400" />
                    <span>{data.active_study_plan.week || "Week 1"}</span>
                  </div>
                  <div>
                    Priority:{" "}
                    <span className="text-indigo-300 font-semibold">
                      {data.active_study_plan.priority || "High"}
                    </span>
                  </div>
                  <div>
                    Progress:{" "}
                    <span className="text-emerald-400 font-semibold">
                      {data.active_study_plan.completed_tasks_count} /{" "}
                      {data.active_study_plan.total_tasks} Tasks
                    </span>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full transition-all"
                    style={{
                      width: `${data.active_study_plan.completion_rate || 0}%`,
                    }}
                  />
                </div>

                {/* Key goals */}
                {data.active_study_plan.goals?.length > 0 && (
                  <div className="bg-slate-900/60 p-3.5 rounded-xl border border-white/5 space-y-2">
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                      Target Objectives
                    </span>
                    <ul className="space-y-1.5 text-xs text-slate-300">
                      {data.active_study_plan.goals.map((g, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <CheckCircle className="w-3.5 h-3.5 text-indigo-400 mt-0.5 shrink-0" />
                          <span>{g}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400 text-sm">
                <Calendar className="w-10 h-10 text-slate-600 mx-auto mb-2" />
                <p>No active study plan generated yet.</p>
                <button
                  onClick={() => setActiveTab("studyplan")}
                  className="btn btn-primary text-xs mt-3 py-1.5 px-3"
                >
                  Generate Personalized Plan
                </button>
              </div>
            )}
          </div>

          {/* Quick Actions Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div
              onClick={() => setActiveTab("chat")}
              className="glass-panel glass-panel-hover p-4 cursor-pointer flex items-center gap-4 group"
            >
              <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center group-hover:scale-105 transition-transform">
                <MessageSquare className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-bold text-white group-hover:text-indigo-400 transition-colors">
                  Ask AI About Notes
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  RAG answers with exact page citations
                </p>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-white transition-colors" />
            </div>

            <div
              onClick={() => setActiveTab("quiz")}
              className="glass-panel glass-panel-hover p-4 cursor-pointer flex items-center gap-4 group"
            >
              <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/20 text-violet-400 flex items-center justify-center group-hover:scale-105 transition-transform">
                <Award className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-bold text-white group-hover:text-violet-400 transition-colors">
                  Test Your Knowledge
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Generate adaptive practice questions
                </p>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-white transition-colors" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
