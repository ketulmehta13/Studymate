import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import {
  Calendar,
  Sparkles,
  CheckCircle,
  Clock,
  BookOpen,
  Plus,
  Trash2,
  AlertCircle,
  TrendingDown,
  Target,
  X,
  ChevronRight,
} from "lucide-react";

export const StudyPlan = () => {
  const [currentPlan, setCurrentPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [generating, setGenerating] = useState(false);

  // Custom plan form state
  const [formData, setFormData] = useState({
    subjects: "",
    exam_date: "",
    available_time: "2 hours/day",
    priority: "High",
  });

  const fetchPlan = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.studyPlan.getLatest();
      setCurrentPlan(res.data);
    } catch (err) {
      setErrorMsg("Failed to load study plan.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlan();
  }, []);

  const handleToggleTask = async (taskIndex) => {
    if (!currentPlan) return;
    try {
      const res = await api.studyPlan.toggleTask(currentPlan.plan_id, taskIndex);
      setCurrentPlan(res.data);
    } catch (err) {
      console.error("Failed to toggle task", err);
    }
  };

  const handleCreatePlan = async (e) => {
    e.preventDefault();
    setGenerating(true);
    setErrorMsg(null);

    const subjectsList = formData.subjects
      ? formData.subjects.split(",").map((s) => s.trim()).filter(Boolean)
      : [];

    try {
      const res = await api.studyPlan.generate({
        subjects: subjectsList,
        exam_date: formData.exam_date,
        available_time: formData.available_time,
        priority: formData.priority,
      });
      setCurrentPlan(res.data);
      setShowCreateModal(false);
    } catch (err) {
      setErrorMsg("Failed to generate plan.");
    } finally {
      setGenerating(false);
    }
  };

  const completedCount = currentPlan?.completed_tasks?.length || 0;
  const totalTasks = currentPlan?.daily_tasks?.length || 0;
  const progressPercent = totalTasks > 0 ? Math.round((completedCount / totalTasks) * 100) : 0;

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white font-['Outfit'] tracking-tight">
            Personalized <span className="text-indigo-400">Study Planner</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Adaptive weekly schedule automatically targeted at your weak topics.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary"
        >
          <Plus className="w-4 h-4" />
          <span>New Target Plan</span>
        </button>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          <span>{errorMsg}</span>
        </div>
      )}

      {loading ? (
        <div className="text-center py-20 text-slate-400">
          <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm">Synthesizing personalized study plan...</p>
        </div>
      ) : currentPlan ? (
        <div className="space-y-8">
          {/* Plan Overview Glass Card */}
          <div className="glass-panel p-6 sm:p-8 border border-white/10 space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="badge badge-indigo text-[10px]">
                    {currentPlan.week || "Week 1"}
                  </span>
                  <span className="badge badge-purple text-[10px]">
                    Priority: {currentPlan.priority || "High"}
                  </span>
                  {currentPlan.exam_date && (
                    <span className="badge badge-amber text-[10px]">
                      Target Exam: {currentPlan.exam_date}
                    </span>
                  )}
                </div>
                <h2 className="text-2xl font-bold text-white">
                  {currentPlan.title}
                </h2>
                {currentPlan.reason && (
                  <p className="text-xs text-slate-400 mt-1 max-w-2xl">
                    {currentPlan.reason}
                  </p>
                )}
              </div>

              {/* Progress Ring / Bar */}
              <div className="bg-slate-900/80 p-4 rounded-2xl border border-white/5 min-w-[200px]">
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-2">
                  <span>Weekly Completion</span>
                  <span className="text-indigo-400">{progressPercent}%</span>
                </div>
                <div className="w-full h-2.5 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 transition-all duration-300"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
                <div className="text-[11px] text-slate-500 mt-2 text-right">
                  {completedCount} of {totalTasks} tasks completed
                </div>
              </div>
            </div>

            {/* Weekly Goals */}
            {currentPlan.goals?.length > 0 && (
              <div className="pt-4 border-t border-white/5">
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-3">
                  Core Weekly Goals
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {currentPlan.goals.map((g, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-start gap-2.5 text-xs text-slate-300"
                    >
                      <Target className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                      <span>{g}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Daily Schedule (Monday to Sunday) */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Calendar className="w-5 h-5 text-indigo-400" />
              <span>Structured Daily Schedule</span>
            </h3>

            <div className="space-y-3">
              {currentPlan.daily_tasks?.map((task, idx) => {
                const isCompleted = currentPlan.completed_tasks?.includes(idx);
                return (
                  <div
                    key={idx}
                    onClick={() => handleToggleTask(idx)}
                    className={`glass-panel p-4 sm:p-5 flex items-start sm:items-center justify-between gap-4 cursor-pointer transition-all border ${
                      isCompleted
                        ? "bg-slate-900/40 border-emerald-500/20 opacity-75"
                        : "border-white/10 hover:border-indigo-500/30"
                    }`}
                  >
                    <div className="flex items-start sm:items-center gap-4">
                      {/* Checkbox */}
                      <button
                        type="button"
                        className={`w-6 h-6 rounded-lg flex items-center justify-center shrink-0 transition-colors mt-0.5 sm:mt-0 ${
                          isCompleted
                            ? "bg-emerald-500 text-white"
                            : "border border-white/20 bg-white/5 hover:border-indigo-400"
                        }`}
                      >
                        {isCompleted && <CheckCircle className="w-4 h-4" />}
                      </button>

                      <div>
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                            {task.day}
                          </span>
                          <span className="badge badge-purple text-[10px]">
                            {task.topic}
                          </span>
                          <span className="badge badge-indigo text-[10px]">
                            <Clock className="w-3 h-3 inline mr-1" />
                            {task.estimated_time}
                          </span>
                        </div>

                        <h4
                          className={`text-sm font-semibold ${
                            isCompleted
                              ? "text-slate-400 line-through"
                              : "text-white"
                          }`}
                        >
                          {task.task}
                        </h4>

                        {task.resources_to_review && (
                          <p className="text-xs text-slate-500 mt-1">
                            Resource: {task.resources_to_review}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="text-right shrink-0 hidden sm:block">
                      <span
                        className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                          task.priority === "High"
                            ? "bg-rose-500/10 text-rose-300 border border-rose-500/20"
                            : "bg-indigo-500/10 text-indigo-300 border border-indigo-500/20"
                        }`}
                      >
                        {task.priority} Priority
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Weak Topics Analysis Section */}
          {currentPlan.topic_analysis?.length > 0 && (
            <div className="glass-panel p-6 sm:p-8 space-y-4 border border-white/10">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <TrendingDown className="w-5 h-5 text-indigo-400" />
                <span>Adaptive Subject Diagnostics</span>
              </h3>
              <p className="text-xs text-slate-400">
                AI analysis of your test history determining this week's prioritized study sessions.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                {currentPlan.topic_analysis.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-white">
                        {item.topic}
                      </span>
                      <span
                        className={`badge ${
                          item.status === "Weak"
                            ? "badge-rose"
                            : item.status === "Moderate"
                            ? "badge-amber"
                            : "badge-green"
                        }`}
                      >
                        {item.status} ({item.accuracy_percentage}%)
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {item.recommendation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="glass-panel p-12 text-center text-slate-400 space-y-3">
          <Calendar className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No active study plan</h3>
          <p className="text-xs max-w-sm mx-auto">
            Generate an adaptive weekly plan tailored to your exam schedule and weak areas.
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn btn-primary text-xs mt-3"
          >
            Create Study Plan
          </button>
        </div>
      )}

      {/* Create Plan Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel max-w-lg w-full p-6 space-y-5 border border-white/20">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                <h3 className="text-lg font-bold text-white">
                  Generate Custom Study Plan
                </h3>
              </div>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreatePlan} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1 uppercase tracking-wider">
                  Target Subjects / Topics (comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Distributed Systems, Dynamic Programming, Neural Networks"
                  value={formData.subjects}
                  onChange={(e) =>
                    setFormData({ ...formData, subjects: e.target.value })
                  }
                  className="input-field text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1 uppercase tracking-wider">
                    Target Exam Date
                  </label>
                  <input
                    type="date"
                    value={formData.exam_date}
                    onChange={(e) =>
                      setFormData({ ...formData, exam_date: e.target.value })
                    }
                    className="input-field text-sm bg-slate-900"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1 uppercase tracking-wider">
                    Daily Study Time
                  </label>
                  <select
                    value={formData.available_time}
                    onChange={(e) =>
                      setFormData({ ...formData, available_time: e.target.value })
                    }
                    className="input-field text-sm bg-slate-900"
                  >
                    <option value="1 hour/day">1 hour/day</option>
                    <option value="2 hours/day">2 hours/day</option>
                    <option value="3 hours/day">3 hours/day</option>
                    <option value="4+ hours/day">4+ hours/day</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1 uppercase tracking-wider">
                  Study Urgency / Priority
                </label>
                <select
                  value={formData.priority}
                  onChange={(e) =>
                    setFormData({ ...formData, priority: e.target.value })
                  }
                  className="input-field text-sm bg-slate-900"
                >
                  <option value="High">High (Impending Exam)</option>
                  <option value="Medium">Medium (Regular Semester Cadence)</option>
                  <option value="Low">Low (Long-Term Mastery)</option>
                </select>
              </div>

              <div className="pt-3 border-t border-white/10 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="btn btn-secondary text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={generating}
                  className="btn btn-primary text-xs"
                >
                  {generating ? "Synthesizing Schedule..." : "Generate Plan"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
