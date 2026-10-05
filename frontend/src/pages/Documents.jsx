import React, { useState, useEffect, useRef } from "react";
import { api } from "../services/api";
import {
  FileText,
  Upload,
  Trash2,
  CheckCircle,
  AlertCircle,
  File,
  Layers,
  Calendar,
  MessageSquare,
  Search,
  Sparkles,
  Eye,
  X,
} from "lucide-react";

export const Documents = ({ setActiveTab }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDoc, setSelectedDoc] = useState(null);

  const fileInputRef = useRef(null);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const res = await api.documents.list();
      setDocuments(res.data);
    } catch (err) {
      setErrorMsg("Failed to load documents.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (file) => {
    if (!file) return;

    setErrorMsg(null);
    setSuccessMsg(null);

    // Validate extension
    const ext = file.name.split(".").pop().toLowerCase();
    if (!["pdf", "txt", "text", "md"].includes(ext)) {
      setErrorMsg("Invalid file format. Only PDF and TXT files are supported.");
      return;
    }

    // Validate size (25MB)
    if (file.size > 25 * 1024 * 1024) {
      setErrorMsg("File exceeds the 25MB upload limit.");
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const res = await api.documents.upload(file, (progressEvent) => {
        const percent = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        setUploadProgress(percent);
      });

      setSuccessMsg(
        `Document "${file.name}" ingested successfully! Classified as ${res.data.topic || "Academic"}.`
      );
      fetchDocuments();
    } catch (err) {
      const msg =
        err.response?.data?.message ||
        err.response?.data?.error ||
        "Failed to process and index the document.";
      setErrorMsg(msg);
    } finally {
      setUploading(false);
      setUploadProgress(0);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (docId, filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) return;

    try {
      await api.documents.delete(docId);
      setSuccessMsg(`Document "${filename}" deleted.`);
      fetchDocuments();
      if (selectedDoc?.document_id === docId) setSelectedDoc(null);
    } catch (err) {
      setErrorMsg("Failed to delete document.");
    }
  };

  const filteredDocs = documents.filter((d) =>
    d.filename?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.topic?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white font-['Outfit'] tracking-tight">
            Study Material <span className="text-indigo-400">& Notes</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Upload your lecture slides, notes, or textbooks to power the RAG AI study assistant.
          </p>
        </div>

        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="btn btn-primary"
        >
          <Upload className="w-4 h-4" />
          <span>Upload PDF or TXT</span>
        </button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => handleFileUpload(e.target.files[0])}
          accept=".pdf,.txt,.text,.md"
          className="hidden"
        />
      </div>

      {/* Alerts */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 flex items-center justify-between text-rose-300 text-sm">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button onClick={() => setErrorMsg(null)} className="text-rose-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-between text-emerald-300 text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 shrink-0" />
            <span>{successMsg}</span>
          </div>
          <button onClick={() => setSuccessMsg(null)} className="text-emerald-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Drag & Drop Upload Dropzone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (e.dataTransfer.files?.[0]) {
            handleFileUpload(e.dataTransfer.files[0]);
          }
        }}
        onClick={() => fileInputRef.current?.click()}
        className={`glass-panel border-2 border-dashed p-8 text-center cursor-pointer transition-all ${
          uploading
            ? "border-indigo-500 bg-indigo-500/5 cursor-wait"
            : "border-white/10 hover:border-indigo-500/50 hover:bg-slate-900/60"
        }`}
      >
        {uploading ? (
          <div className="max-w-md mx-auto space-y-4">
            <div className="w-12 h-12 rounded-full border-3 border-indigo-500/30 border-t-indigo-500 animate-spin mx-auto" />
            <div>
              <p className="text-sm font-semibold text-white">
                Ingesting and Vectorizing Study Material...
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Extracting text, classifying domain topic, and generating FAISS embeddings
              </p>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
              <Upload className="w-7 h-7" />
            </div>
            <div>
              <p className="text-base font-semibold text-white">
                Drop your PDF or TXT notes here, or <span className="text-indigo-400">browse</span>
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Supports lecture slides, textbook chapters, and revision sheets up to 25MB
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Search Bar & Document Count */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
          <input
            type="text"
            placeholder="Search notes by title or academic topic..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        <div className="text-xs text-slate-400 self-center">
          Showing <span className="text-white font-semibold">{filteredDocs.length}</span> documents
        </div>
      </div>

      {/* Documents Grid */}
      {loading ? (
        <div className="text-center py-16 text-slate-400 space-y-3">
          <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto" />
          <p className="text-sm">Loading your study documents...</p>
        </div>
      ) : filteredDocs.length === 0 ? (
        <div className="glass-panel p-12 text-center text-slate-400 space-y-3">
          <FileText className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No documents found</h3>
          <p className="text-xs max-w-sm mx-auto">
            {searchQuery
              ? "No study notes matched your search query."
              : "Upload your first study document above to start asking questions with the AI assistant."}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredDocs.map((doc) => {
            const isPdf = doc.file_type === "pdf" || doc.filename?.endsWith(".pdf");
            return (
              <div
                key={doc.document_id}
                className="glass-panel glass-panel-hover p-5 flex flex-col justify-between group"
              >
                <div>
                  {/* Card Header: Type badge & Actions */}
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <span
                      className={`badge ${
                        isPdf ? "badge-rose" : "badge-indigo"
                      }`}
                    >
                      {doc.file_type?.toUpperCase() || (isPdf ? "PDF" : "TXT")}
                    </span>

                    {doc.topic && (
                      <span className="badge badge-purple text-[10px]">
                        {doc.topic}
                      </span>
                    )}
                  </div>

                  {/* Title */}
                  <h3
                    title={doc.filename}
                    className="text-base font-bold text-white truncate group-hover:text-indigo-300 transition-colors"
                  >
                    {doc.filename}
                  </h3>

                  {/* Metadata Chips */}
                  <div className="grid grid-cols-2 gap-2 mt-4 text-xs text-slate-400">
                    <div className="flex items-center gap-1.5">
                      <File className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{doc.page_count || 1} Pages</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-violet-400" />
                      <span>{doc.chunks_count || 0} Chunks</span>
                    </div>
                    <div className="flex items-center gap-1.5 col-span-2">
                      <Calendar className="w-3.5 h-3.5 text-slate-500" />
                      <span>
                        {doc.created_at
                          ? new Date(doc.created_at).toLocaleDateString()
                          : "Recently"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Footer Buttons */}
                <div className="mt-5 pt-4 border-t border-white/5 flex items-center justify-between gap-2">
                  <button
                    onClick={() => {
                      setActiveTab("chat");
                    }}
                    className="btn btn-primary text-xs py-1.5 px-3 flex-1"
                  >
                    <MessageSquare className="w-3.5 h-3.5" />
                    <span>Ask AI</span>
                  </button>

                  <button
                    onClick={() => setSelectedDoc(doc)}
                    title="View Document Details"
                    className="p-2 rounded-lg bg-white/5 text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => handleDelete(doc.document_id, doc.filename)}
                    title="Delete Document"
                    className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Document Detail Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel max-w-lg w-full p-6 space-y-4 border border-white/20">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-400" />
                <h3 className="text-lg font-bold text-white truncate max-w-xs">
                  {selectedDoc.filename}
                </h3>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-300">
              <div className="flex justify-between py-1.5 border-b border-white/5">
                <span className="text-slate-400">Document ID:</span>
                <span className="font-mono text-[11px] text-slate-200">
                  {selectedDoc.document_id}
                </span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-white/5">
                <span className="text-slate-400">Academic Topic:</span>
                <span className="badge badge-purple">{selectedDoc.topic || "General"}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-white/5">
                <span className="text-slate-400">Total Pages:</span>
                <span>{selectedDoc.page_count}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-white/5">
                <span className="text-slate-400">RAG Vector Chunks:</span>
                <span>{selectedDoc.chunks_count} indexed chunks</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-white/5">
                <span className="text-slate-400">Processing Status:</span>
                <span className="badge badge-green">Ready for RAG</span>
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <button
                onClick={() => setSelectedDoc(null)}
                className="btn btn-secondary text-xs"
              >
                Close
              </button>
              <button
                onClick={() => {
                  setSelectedDoc(null);
                  setActiveTab("chat");
                }}
                className="btn btn-primary text-xs"
              >
                <MessageSquare className="w-3.5 h-3.5" />
                Ask Questions
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
