import { useState } from 'react'
import { useAuth } from './context/AuthContext'
import { AuthPage } from './components/AuthPage'
import { Navbar } from './components/Navbar'
import { Dashboard } from './pages/Dashboard'
import { Documents } from './pages/Documents'
import { Chat } from './pages/Chat'
import { Quiz } from './pages/Quiz'
import { StudyPlan } from './pages/StudyPlan'
import { api } from './services/api'
import {
  Sparkles,
  Brain,
  AlertCircle,
  Loader2,
  Send,
  BarChart3,
  Target,
  FileText,
  TrendingUp,
  BookOpen,
} from 'lucide-react'

/* ─── Topic Classifier Page ─── */
const TopicClassifier = () => {
  const [inputText, setInputText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [modelStatus, setModelStatus] = useState(null)

  const handleClassify = async () => {
    if (!inputText.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await api.classifier.predict(inputText)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.message || 'Classification failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const checkStatus = async () => {
    try {
      const res = await api.classifier.status()
      setModelStatus(res.data)
    } catch {
      setModelStatus({ status: 'unavailable' })
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      <div className="glass-panel p-6 sm:p-8 border border-white/10">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-violet-500/15 border border-violet-500/25 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">ML Topic Classifier</h1>
            <p className="text-xs text-slate-400">
              Classical ML model — predicts the academic subject of any text passage.
            </p>
          </div>
        </div>

        <div className="space-y-4 mt-6">
          <textarea
            className="input-field min-h-[120px] resize-y"
            placeholder="Paste any passage from your study notes, syllabus, or textbook..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
          />

          <div className="flex items-center gap-3">
            <button
              onClick={handleClassify}
              disabled={loading || !inputText.trim()}
              className="btn btn-primary"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Classify Topic</span>
                </>
              )}
            </button>

            <button
              onClick={checkStatus}
              className="btn btn-secondary text-xs"
            >
              Check Model Status
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 flex items-start gap-2.5 text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {result && (
          <div className="mt-6 glass-panel p-5 border border-indigo-500/20">
            <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <Target className="w-4 h-4 text-indigo-400" />
              Classification Result
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
                  Predicted Topic
                </span>
                <span className="badge badge-indigo">{result.predicted_topic || result.topic}</span>
              </div>
              {result.confidence !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
                    Confidence
                  </span>
                  <span className="text-emerald-400 font-bold text-sm">
                    {(result.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              )}
              {result.top_predictions && (
                <div className="mt-3 pt-3 border-t border-white/5 space-y-2">
                  <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
                    All Predictions
                  </span>
                  {result.top_predictions.map((pred, i) => (
                    <div key={i} className="flex items-center justify-between text-xs">
                      <span className="text-slate-300">{pred.topic || pred.label}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500"
                            style={{ width: `${(pred.confidence || pred.score) * 100}%` }}
                          />
                        </div>
                        <span className="text-slate-400 w-12 text-right">
                          {((pred.confidence || pred.score) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {modelStatus && (
          <div className="mt-4 p-3.5 rounded-xl bg-slate-900/60 border border-white/5 text-xs text-slate-300 space-y-1">
            <div>
              <span className="font-semibold text-slate-400">Model Status: </span>
              <span className={modelStatus.status === 'ready' ? 'text-emerald-400' : 'text-amber-400'}>
                {modelStatus.status}
              </span>
            </div>
            {modelStatus.model_type && (
              <div>
                <span className="font-semibold text-slate-400">Model Type: </span>
                <span>{modelStatus.model_type}</span>
              </div>
            )}
            {modelStatus.topics && (
              <div>
                <span className="font-semibold text-slate-400">Topics: </span>
                <span>{modelStatus.topics.join(', ')}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

/* ─── Progress / Analytics Page ─── */
const ProgressAnalytics = () => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useState(() => {
    const fetchProgress = async () => {
      try {
        const res = await api.progress.getSummary()
        setData(res.data)
      } catch (err) {
        setError('Failed to load progress data.')
      } finally {
        setLoading(false)
      }
    }
    fetchProgress()
  })

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto flex flex-col items-center justify-center py-24 text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-400 mb-3" />
        <span className="text-sm">Loading analytics...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto py-12">
        <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      </div>
    )
  }

  const m = data?.metrics || {}

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      <div className="glass-panel p-6 sm:p-8 border border-white/10">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/25 flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Learning Progress</h1>
            <p className="text-xs text-slate-400">
              Track your study statistics, quiz performance, and topic mastery.
            </p>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="glass-panel p-4 text-center">
            <FileText className="w-6 h-6 text-indigo-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{m.documents_uploaded || 0}</div>
            <div className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold mt-1">
              Documents
            </div>
          </div>
          <div className="glass-panel p-4 text-center">
            <BookOpen className="w-6 h-6 text-violet-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{m.quizzes_completed || 0}</div>
            <div className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold mt-1">
              Quizzes Done
            </div>
          </div>
          <div className="glass-panel p-4 text-center">
            <TrendingUp className="w-6 h-6 text-emerald-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{m.average_quiz_score || 0}%</div>
            <div className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold mt-1">
              Avg. Score
            </div>
          </div>
          <div className="glass-panel p-4 text-center">
            <Brain className="w-6 h-6 text-cyan-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{m.questions_asked || 0}</div>
            <div className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold mt-1">
              AI Questions
            </div>
          </div>
        </div>

        {/* Topic Mastery */}
        <div className="glass-panel p-5 border border-white/5">
          <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <Target className="w-4 h-4 text-indigo-400" />
            Topic Mastery Breakdown
          </h2>
          {data?.topic_mastery && Object.keys(data.topic_mastery).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(data.topic_mastery).map(([topic, pct]) => (
                <div key={topic} className="space-y-1.5">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-300">{topic}</span>
                    <span
                      className={
                        pct >= 75 ? 'text-emerald-400' : pct >= 50 ? 'text-amber-400' : 'text-rose-400'
                      }
                    >
                      {pct}%
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        pct >= 75
                          ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                          : pct >= 50
                          ? 'bg-gradient-to-r from-amber-500 to-yellow-400'
                          : 'bg-gradient-to-r from-rose-500 to-pink-500'
                      }`}
                      style={{ width: `${Math.min(100, Math.max(5, pct))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400 text-center py-6">
              No quiz results yet. Take some quizzes to see your topic mastery!
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

/* ─── Main App Shell ─── */
function App() {
  const { isAuthenticated, isLoading } = useAuth()
  const [activeTab, setActiveTab] = useState('dashboard')

  // Show loading spinner during auth verification
  if (isLoading) {
    return (
      <div className="aurora-bg min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-500 flex items-center justify-center shadow-xl shadow-indigo-500/30 animate-pulse">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <div className="flex items-center gap-2 text-slate-400 text-sm">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Loading StudyMate AI...</span>
          </div>
        </div>
      </div>
    )
  }

  // Show login/register page if not authenticated
  if (!isAuthenticated) {
    return <AuthPage />
  }

  // Render active page content
  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard setActiveTab={setActiveTab} />
      case 'documents':
        return <Documents setActiveTab={setActiveTab} />
      case 'chat':
        return <Chat />
      case 'quiz':
        return <Quiz />
      case 'studyplan':
        return <StudyPlan />
      case 'classifier':
        return <TopicClassifier />
      case 'analytics':
        return <ProgressAnalytics />
      default:
        return <Dashboard setActiveTab={setActiveTab} />
    }
  }

  return (
    <div className="aurora-bg min-h-screen">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="px-2 sm:px-6">
        {renderPage()}
      </main>
    </div>
  )
}

export default App
