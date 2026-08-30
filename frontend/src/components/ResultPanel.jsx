import ConfidenceBadge from "./ConfidenceBadge.jsx";
import MarkdownView from "./MarkdownView.jsx";

function MetaRow({ label, value, mono = false }) {
  return (
    <div className="flex items-baseline gap-2">
      <span className="text-[11px] uppercase tracking-wider text-slate-500 w-24 shrink-0">
        {label}
      </span>
      <span
        className={`text-sm text-slate-200 ${mono ? "font-mono text-[13px]" : ""}`}
      >
        {value || "—"}
      </span>
    </div>
  );
}

export default function ResultPanel({ result, onOpenSource }) {
  if (!result) return null;

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Summary card */}
      <section className="rounded-xl border border-bg-700 bg-bg-900 p-4">
        <div className="flex flex-wrap items-center gap-3 mb-3">
          <div>
            <p className="text-[11px] uppercase tracking-wider text-slate-500">Error Detected</p>
            <p className="text-lg font-bold text-slate-100 font-mono">
              {result.detected_error}
            </p>
          </div>
          <div className="ml-auto">
            <ConfidenceBadge level={result.confidence} reason={result.confidence_reason} />
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 border-t border-bg-700 pt-3">
          <MetaRow label="Language" value={result.language} />
          <MetaRow label="Category" value={result.category} />
          <MetaRow label="Error Type" value={result.error_type} mono />
        </div>

        {result.confidence_reason && (
          <p className="mt-3 text-xs text-slate-500">
            <span className="text-slate-400">Why:</span> {result.confidence_reason}
          </p>
        )}

        {result.keywords?.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {result.keywords.map((k) => (
              <span
                key={k}
                className="px-2 py-0.5 rounded-full text-[11px] font-mono bg-bg-800 border border-bg-700 text-cyan-300"
              >
                {k}
              </span>
            ))}
            {result.rag_query && (
              <span className="px-2 py-0.5 rounded-full text-[11px] bg-bg-800 text-slate-500 border border-dashed border-bg-700">
                query: {result.rag_query}
              </span>
            )}
          </div>
        )}

        {result.warnings?.length > 0 && (
          <div className="mt-3 space-y-1">
            {result.warnings.map((w, i) => (
              <p key={i} className="text-xs text-warn flex items-start gap-1.5">
                <span>⚠</span>
                <span>{w}</span>
              </p>
            ))}
          </div>
        )}
      </section>

      {/* Diagnosis */}
      <section className="rounded-xl border border-bg-700 bg-bg-900 p-4 sm:p-5">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-cyan-400">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="M9 3h6l1 3h4v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6h4l1-3Z"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinejoin="round"
              />
              <path d="M9.5 14l1.8 1.8L15.5 12" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </span>
          <h2 className="text-sm font-semibold text-slate-100">Diagnosis</h2>
          <button
            onClick={onOpenSource}
            className="ml-auto text-[11px] text-accent-400 hover:text-accent-300"
          >
            View sources →
          </button>
        </div>
        <MarkdownView content={result.diagnosis} />
      </section>
    </div>
  );
}