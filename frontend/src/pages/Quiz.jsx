import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import {
  Award,
  Sparkles,
  CheckCircle,
  XCircle,
  Clock,
  ArrowRight,
  ArrowLeft,
  RotateCcw,
  BookOpen,
  History,
  AlertCircle,
  Check,
} from "lucide-react";

export const Quiz = () => {
  const [activeTab, setActiveTab] = useState("generator"); // 'generator' | 'active' | 'results' | 'history'

  // Generator form state
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("medium");
  const [questionCount, setQuestionCount] = useState(5);
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState(null);

  // Active quiz state
  const [currentQuiz, setCurrentQuiz] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Results state
  const [quizResult, setQuizResult] = useState(null);

  // History state
  const [historyList, setHistoryList] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await api.quiz.history();
      setHistoryList(res.data);
    } catch (err) {
      console.error("Failed to load quiz history", err);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "history") {
      fetchHistory();
    }
  }, [activeTab]);

  const handleGenerate = async (topicToUse = null) => {
    const targetTopic = topicToUse || topic;
    if (!targetTopic.trim()) {
      setGenError("Please enter a study topic.");
      return;
    }

    setGenerating(true);
    setGenError(null);

    try {
      const res = await api.quiz.generate(targetTopic.trim(), difficulty, questionCount);
      setCurrentQuiz(res.data);
      setSelectedAnswers({});
      setCurrentQuestionIndex(0);
      setActiveTab("active");
    } catch (err) {
      const msg =
        err.response?.data?.message ||
        err.response?.data?.error ||
        "Failed to generate quiz. Please try again.";
      setGenError(msg);
    } finally {
      setGenerating(false);
    }
  };

  const handleSelectOption = (questionIdx, optionText) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [String(questionIdx)]: optionText,
    }));
  };

  const handleSubmitQuiz = async () => {
    if (!currentQuiz) return;
    setSubmitting(true);

    try {
      const res = await api.quiz.submit(currentQuiz.quiz_id, selectedAnswers);
      setQuizResult(res.data);
      setActiveTab("results");
    } catch (err) {
      alert("Failed to submit quiz. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const quickTopics = [
    "Machine Learning",
    "Natural Language Processing",
    "Data Structures",
    "Database Systems",
    "Algorithms",
    "Linear Algebra",
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Header & Mode Switcher */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white font-['Outfit'] tracking-tight">
            Practice <span className="text-indigo-400">Quizzes</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Adaptive AI multiple-choice quizzes grounded in your course notes.
          </p>
        </div>

        <div className="flex bg-slate-900/80 p-1 rounded-xl border border-white/10 self-stretch sm:self-auto">
          <button
            onClick={() => setActiveTab("generator")}
            className={`flex-1 sm:flex-none px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
              activeTab === "generator" || activeTab === "active" || activeTab === "results"
                ? "bg-indigo-600 text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Quiz Creator
          </button>
          <button
            onClick={() => setActiveTab("history")}
            className={`flex-1 sm:flex-none px-4 py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              activeTab === "history"
                ? "bg-indigo-600 text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Past Results</span>
          </button>
        </div>
      </div>

      {/* Mode 1: Quiz Generator */}
      {activeTab === "generator" && (
        <div className="glass-panel p-6 sm:p-8 space-y-6 border border-white/10">
          <div>
            <span className="badge badge-indigo text-[10px] mb-2">Configure Practice</span>
            <h2 className="text-xl font-bold text-white">Generate Structured AI Quiz</h2>
            <p className="text-xs text-slate-400 mt-1">
              Select an academic topic from your notes or enter any custom subject to test your conceptual mastery.
            </p>
          </div>

          {genError && (
            <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 flex items-center gap-2 text-xs text-rose-300">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{genError}</span>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                Topic or Subject
              </label>
              <input
                type="text"
                placeholder="e.g. Overfitting & Regularization, Sorting Algorithms..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="input-field"
              />
            </div>

            {/* Quick Topic Chips */}
            <div>
              <span className="text-xs text-slate-400 block mb-2 font-medium">
                Suggested Coursework Topics:
              </span>
              <div className="flex flex-wrap gap-2">
                {quickTopics.map((t, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      setTopic(t);
                    }}
                    className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
                      topic === t
                        ? "bg-indigo-600 text-white border-indigo-500"
                        : "bg-slate-900/60 text-slate-300 border-white/10 hover:border-white/20"
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                  Difficulty
                </label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="input-field cursor-pointer bg-slate-900"
                >
                  <option value="easy">Easy (Definitions & Foundations)</option>
                  <option value="medium">Medium (Analytical & Problem-Solving)</option>
                  <option value="hard">Hard (Advanced Theory & Application)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                  Number of Questions
                </label>
                <select
                  value={questionCount}
                  onChange={(e) => setQuestionCount(Number(e.target.value))}
                  className="input-field cursor-pointer bg-slate-900"
                >
                  <option value={3}>3 Questions (Quick Check)</option>
                  <option value={5}>5 Questions (Standard)</option>
                  <option value={10}>10 Questions (Comprehensive Exam)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-white/10">
            <button
              onClick={() => handleGenerate()}
              disabled={generating}
              className="btn btn-primary w-full py-3 text-base font-semibold"
            >
              {generating ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Synthesizing Questions from Notes...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  <span>Generate Practice Quiz</span>
                </div>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Mode 2: Active Quiz Taking */}
      {activeTab === "active" && currentQuiz && (
        <div className="glass-panel p-6 sm:p-8 space-y-6 border border-white/10">
          {/* Progress bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold text-white">
                Question {currentQuestionIndex + 1} of {currentQuiz.questions?.length}
              </span>
              <span className="badge badge-purple text-[10px]">
                {currentQuiz.topic} • {currentQuiz.difficulty}
              </span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all duration-300"
                style={{
                  width: `${
                    ((currentQuestionIndex + 1) / (currentQuiz.questions?.length || 1)) *
                    100
                  }%`,
                }}
              />
            </div>
          </div>

          {/* Question Box */}
          {(() => {
            const q = currentQuiz.questions[currentQuestionIndex];
            const currentSelected = selectedAnswers[String(currentQuestionIndex)];
            const isLastQuestion =
              currentQuestionIndex === currentQuiz.questions.length - 1;

            return (
              <div className="space-y-6">
                <h3 className="text-lg sm:text-xl font-bold text-white leading-relaxed">
                  {q.question}
                </h3>

                {/* Multiple Choice Options */}
                <div className="space-y-3">
                  {q.options.map((option, optIdx) => {
                    const letters = ["A", "B", "C", "D"];
                    const isSelected = currentSelected === option;
                    return (
                      <button
                        key={optIdx}
                        onClick={() =>
                          handleSelectOption(currentQuestionIndex, option)
                        }
                        className={`w-full text-left p-4 rounded-xl border transition-all flex items-center gap-3.5 ${
                          isSelected
                            ? "bg-indigo-600/25 border-indigo-500 text-white shadow-md shadow-indigo-500/10"
                            : "bg-slate-900/60 border-white/10 text-slate-300 hover:border-white/20 hover:bg-slate-900"
                        }`}
                      >
                        <div
                          className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 ${
                            isSelected
                              ? "bg-indigo-600 text-white"
                              : "bg-white/5 text-slate-400"
                          }`}
                        >
                          {letters[optIdx]}
                        </div>
                        <span className="text-sm font-medium leading-relaxed">
                          {option}
                        </span>
                      </button>
                    );
                  })}
                </div>

                {/* Nav Buttons */}
                <div className="flex items-center justify-between pt-4 border-t border-white/10">
                  <button
                    disabled={currentQuestionIndex === 0}
                    onClick={() => setCurrentQuestionIndex((prev) => prev - 1)}
                    className="btn btn-secondary text-xs"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    <span>Previous</span>
                  </button>

                  {isLastQuestion ? (
                    <button
                      onClick={handleSubmitQuiz}
                      disabled={submitting}
                      className="btn btn-primary text-sm font-semibold px-6"
                    >
                      {submitting ? "Grading..." : "Submit Quiz"}
                    </button>
                  ) : (
                    <button
                      onClick={() => setCurrentQuestionIndex((prev) => prev + 1)}
                      className="btn btn-primary text-xs"
                    >
                      <span>Next Question</span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* Mode 3: Quiz Results & Detailed Explanation */}
      {activeTab === "results" && quizResult && (
        <div className="glass-panel p-6 sm:p-8 space-y-8 border border-white/10">
          {/* Top Score Banner */}
          <div className="text-center space-y-3 pb-6 border-b border-white/10">
            <div className="inline-flex w-20 h-20 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 items-center justify-center text-3xl font-extrabold text-white shadow-xl shadow-indigo-500/30">
              {quizResult.percentage}%
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">
                {quizResult.percentage >= 80
                  ? "Outstanding Performance!"
                  : quizResult.percentage >= 60
                  ? "Good Progress!"
                  : "Review Recommended"}
              </h2>
              <p className="text-sm text-slate-400 mt-1">
                You answered{" "}
                <strong className="text-white">
                  {quizResult.score} of {quizResult.total_questions}
                </strong>{" "}
                questions correctly on <em>{quizResult.topic}</em>.
              </p>
            </div>

            <div className="flex justify-center gap-3 pt-2">
              <button
                onClick={() => setActiveTab("generator")}
                className="btn btn-primary text-xs"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Take Another Quiz</span>
              </button>
              <button
                onClick={() => setActiveTab("history")}
                className="btn btn-secondary text-xs"
              >
                View History
              </button>
            </div>
          </div>

          {/* Detailed Question Review */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-indigo-400" />
              <span>Question Review & Explanations</span>
            </h3>

            {quizResult.detailed_results?.map((res, idx) => (
              <div
                key={idx}
                className={`p-5 rounded-xl border space-y-3 ${
                  res.is_correct
                    ? "bg-emerald-500/5 border-emerald-500/30"
                    : "bg-rose-500/5 border-rose-500/30"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <h4 className="text-sm font-semibold text-white">
                    {idx + 1}. {res.question}
                  </h4>
                  {res.is_correct ? (
                    <span className="badge badge-green shrink-0">Correct</span>
                  ) : (
                    <span className="badge badge-rose shrink-0">Incorrect</span>
                  )}
                </div>

                <div className="text-xs space-y-1.5 pl-2 border-l-2 border-white/10">
                  <div>
                    <span className="text-slate-400">Your Answer: </span>
                    <span
                      className={
                        res.is_correct ? "text-emerald-300 font-semibold" : "text-rose-300 font-semibold"
                      }
                    >
                      {res.user_answer || "(No answer provided)"}
                    </span>
                  </div>

                  {!res.is_correct && (
                    <div>
                      <span className="text-slate-400">Correct Answer: </span>
                      <span className="text-emerald-300 font-semibold">
                        {res.correct_answer}
                      </span>
                    </div>
                  )}

                  {res.explanation && (
                    <p className="text-slate-300 pt-1 leading-relaxed">
                      <strong>Explanation:</strong> {res.explanation}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Mode 4: Past Results History */}
      {activeTab === "history" && (
        <div className="glass-panel p-6 space-y-6 border border-white/10">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <History className="w-5 h-5 text-indigo-400" />
              <span>Quiz Attempt History</span>
            </h2>
            <button
              onClick={() => setActiveTab("generator")}
              className="btn btn-primary text-xs"
            >
              New Quiz
            </button>
          </div>

          {historyLoading ? (
            <div className="text-center py-12 text-slate-400">
              <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto mb-2" />
              <p className="text-xs">Loading past submissions...</p>
            </div>
          ) : historyList.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-sm">
              <Award className="w-10 h-10 text-slate-600 mx-auto mb-2" />
              <p>No past quizzes completed yet.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {historyList.map((item, idx) => (
                <div
                  key={idx}
                  className="glass-panel p-4 flex items-center justify-between gap-4 border border-white/5"
                >
                  <div>
                    <h4 className="text-sm font-bold text-white">{item.topic}</h4>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {item.score} / {item.total_questions} questions correct •{" "}
                      {item.created_at
                        ? new Date(item.created_at).toLocaleDateString()
                        : "Recently"}
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={`text-sm font-extrabold px-3 py-1 rounded-full ${
                        item.percentage >= 75
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          : item.percentage >= 50
                          ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                          : "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                      }`}
                    >
                      {item.percentage}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
