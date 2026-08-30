import { useEffect, useState } from "react";
import { getDocument } from "../services/api.js";
import MarkdownView from "./MarkdownView.jsx";

/**
 * Modal that shows the full text of a knowledge-base Markdown document
 * (fetched live from GET /api/documents/{filename}).
 */
export default function DocumentModal({ filename, onClose }) {
  const [content, setContent] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!filename) return;
    let cancelled = false;
    setContent(null);
    setError(null);
    getDocument(filename)
      .then((doc) => {
        if (!cancelled) setContent(doc.content);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [filename]);

  if (!filename) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-label={`Knowledge document ${filename}`}
    >
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="relative w-full max-w-3xl max-h-[85vh] flex flex-col rounded-xl border border-bg-700 bg-bg-900 shadow-2xl">
        <div className="px-4 py-3 border-b border-bg-700 flex items-center gap-2">
          <span className="text-cyan-400">📄</span>
          <h3 className="font-mono text-sm text-slate-100 flex-1 truncate">{filename}</h3>
          <span className="text-[11px] text-slate-500">knowledge base document</span>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-md bg-bg-800 hover:bg-bg-700 text-slate-300 text-lg leading-none"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <div className="overflow-y-auto p-4 sm:p-6 flex-1">
          {error && (
            <p className="text-sm text-danger">Could not load document: {error}</p>
          )}
          {!content && !error && (
            <p className="text-sm text-slate-500 animate-pulse">Loading document…</p>
          )}
          {content && <MarkdownView content={content} />}
        </div>
      </div>
    </div>
  );
}