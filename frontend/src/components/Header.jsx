export default function Header({ backend }) {
  const status = backend.ok
    ? `Backend online · ${backend.info.documents_indexed ?? 0} chunks indexed`
    : backend.ok === false
      ? "Backend offline"
      : "Connecting…";

  return (
    <header className="sticky top-0 z-40 border-b border-bg-800 bg-bg-950/80 backdrop-blur">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 flex items-center gap-3 h-16">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-accent-600/20 border border-accent-500/40 flex items-center justify-center shadow-glow">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="M12 3c3.3 0 6 2.7 6 6 0 2.6-1.6 4.8-3.9 5.7-.6 2-2.1 3.6-4.1 4.2-.3.2-.6-.1-.5-.4.3-1.3 0-2.2-1.1-3.2-1.5-1.4-2.4-3.4-2.4-5.7C6 5.7 8.7 3 12 3Z"
                stroke="#22d3ee"
                strokeWidth="1.6"
                strokeLinejoin="round"
              />
              <circle cx="12" cy="9" r="1.6" fill="#22d3ee" />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-slate-100 leading-tight">
              Error<span className="text-accent-400">Lens</span>
            </h1>
            <p className="text-[11px] text-slate-500 leading-tight">
              AI Error Diagnosis · RAG powered
            </p>
          </div>
        </div>

        <div className="ml-auto flex items-center gap-2 text-xs">
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border ${
              backend.ok
                ? "text-success border-success/30 bg-success/10"
                : backend.ok === false
                  ? "text-danger border-danger/30 bg-danger/10"
                  : "text-slate-400 border-bg-700 bg-bg-800"
            }`}
            title="Backend status"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
            {status}
          </span>
        </div>
      </div>
    </header>
  );
}