import React, { useState, useEffect, useRef } from "react";
import { api } from "../services/api";
import {
  Send,
  Brain,
  User,
  Sparkles,
  FileText,
  ExternalLink,
  Copy,
  Check,
  RotateCcw,
  BookOpen,
  AlertCircle,
  HelpCircle,
} from "lucide-react";

export const Chat = () => {
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      sender: "ai",
      text: "Hello! I am your StudyMate AI assistant. I can answer questions directly from your uploaded lecture notes, explain complex concepts, solve problems with the safe calculator, or search academic web sources when needed. What are you studying today?",
      source_type: "system",
      sources: [],
      timestamp: new Date().toISOString(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(() => `conv_${Date.now()}`);
  const [copiedId, setCopiedId] = useState(null);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend = null) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || loading) return;

    const userMsgId = `user_${Date.now()}`;
    const newMsg = {
      id: userMsgId,
      sender: "user",
      text: text.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, newMsg]);
    setInputMessage("");
    setLoading(true);

    try {
      const res = await api.chat.send(text.trim(), conversationId);
      const aiResponse = {
        id: `ai_${Date.now()}`,
        sender: "ai",
        text: res.data.answer,
        source_type: res.data.source_type,
        sources: res.data.sources || [],
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    } catch (err) {
      const errorMsg = {
        id: `err_${Date.now()}`,
        sender: "ai",
        text: "I encountered an issue processing your question. Please verify your connection or try again.",
        source_type: "error",
        sources: [],
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleResetChat = () => {
    setConversationId(`conv_${Date.now()}`);
    setMessages([
      {
        id: "welcome",
        sender: "ai",
        text: "Session cleared! Ask me anything based on your uploaded study notes.",
        source_type: "system",
        sources: [],
        timestamp: new Date().toISOString(),
      },
    ]);
  };

  const samplePrompts = [
    "What is machine learning according to my notes?",
    "Explain overfitting and methods to prevent it",
    "Calculate the gradient descent step: 10 - (0.01 * 50)",
    "What are the key differences between supervised and unsupervised learning?",
  ];

  return (
    <div className="max-w-5xl mx-auto h-[calc(100vh-140px)] flex flex-col pb-4">
      {/* Chat Header */}
      <div className="glass-panel p-4 mb-4 flex items-center justify-between border border-white/10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <Brain className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <span>StudyMate RAG Assistant</span>
              <span className="badge badge-indigo text-[10px]">LangGraph</span>
            </h2>
            <p className="text-xs text-slate-400">
              Context-grounded answering with exact source citations
            </p>
          </div>
        </div>

        <button
          onClick={handleResetChat}
          title="New Study Session"
          className="btn btn-secondary text-xs py-1.5 px-3"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>New Session</span>
        </button>
      </div>

      {/* Messages Thread Container */}
      <div className="flex-1 glass-panel p-4 sm:p-6 overflow-y-auto space-y-5 border border-white/10">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 ${
              msg.sender === "user" ? "flex-row-reverse" : "flex-row"
            }`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                msg.sender === "user"
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-800 border border-indigo-500/30 text-indigo-400"
              }`}
            >
              {msg.sender === "user" ? (
                <User className="w-4 h-4" />
              ) : (
                <Brain className="w-4 h-4" />
              )}
            </div>

            {/* Bubble */}
            <div
              className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 text-sm leading-relaxed ${
                msg.sender === "user"
                  ? "bg-indigo-600 text-white rounded-tr-none shadow-md shadow-indigo-600/20"
                  : "bg-slate-900/90 border border-white/10 text-slate-200 rounded-tl-none shadow-lg"
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>

              {/* Citations & Sources (if any) */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3.5 pt-3 border-t border-white/10 space-y-2">
                  <div className="flex items-center gap-1.5 text-[11px] font-semibold text-indigo-300">
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>Cited Sources from Your Material:</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {msg.sources.map((src, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-200"
                      >
                        {src.url ? (
                          <a
                            href={src.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 hover:underline"
                          >
                            <span>{src.title || src.url}</span>
                            <ExternalLink className="w-3 h-3 text-slate-400" />
                          </a>
                        ) : (
                          <>
                            <FileText className="w-3.5 h-3.5 text-indigo-400" />
                            <span className="font-medium">{src.filename}</span>
                            <span className="text-slate-400">
                              (Page {src.page})
                            </span>
                          </>
                        )}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Message Footer (Copy button for AI) */}
              {msg.sender === "ai" && (
                <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-400">
                  <span className="capitalize">
                    Source:{" "}
                    <strong className="text-slate-300">
                      {msg.source_type === "web" ? "External Web Search" : "Course Notes"}
                    </strong>
                  </span>
                  <button
                    onClick={() => copyToClipboard(msg.text, msg.id)}
                    className="flex items-center gap-1 text-slate-400 hover:text-white transition-colors"
                  >
                    {copiedId === msg.id ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-400" />
                        <span className="text-emerald-400">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-xl bg-slate-800 border border-indigo-500/30 text-indigo-400 flex items-center justify-center shrink-0">
              <Brain className="w-4 h-4 animate-pulse" />
            </div>
            <div className="bg-slate-900/90 border border-white/10 rounded-2xl rounded-tl-none p-4 text-xs text-slate-400 flex items-center gap-3">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" />
                <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:0.2s]" />
                <span className="w-2 h-2 rounded-full bg-indigo-300 animate-bounce [animation-delay:0.4s]" />
              </div>
              <span>Searching notes & evaluating context...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Pills (visible when conversation is short) */}
      {messages.length <= 3 && (
        <div className="my-2.5 flex flex-wrap gap-2 items-center">
          <span className="text-xs text-slate-400 flex items-center gap-1 mr-1">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" /> Suggestions:
          </span>
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(p)}
              className="text-xs px-3 py-1.5 rounded-full bg-slate-900/80 hover:bg-indigo-600/30 text-slate-300 hover:text-white border border-white/10 transition-colors"
            >
              {p}
            </button>
          ))}
        </div>
      )}

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="glass-panel p-2 sm:p-3 mt-2 flex items-center gap-2 border border-white/10"
      >
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask a question about your study notes..."
          className="flex-1 bg-transparent px-3 py-2 text-sm text-white focus:outline-none placeholder:text-slate-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !inputMessage.trim()}
          className="btn btn-primary py-2 px-4 text-sm"
        >
          <Send className="w-4 h-4" />
          <span className="hidden sm:inline">Send</span>
        </button>
      </form>
    </div>
  );
};
