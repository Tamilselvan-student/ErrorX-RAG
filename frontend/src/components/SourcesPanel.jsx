const RELEVANCE_STYLES = {
  High: "text-success",
  Medium: "text-warn",
  Low: "text-slate-400",
};

export default function SourcesPanel({ sources, onOpen }) {
  if (!sources || sources.length === 0) return null;

  return (
    <section className="rounded-xl border border-bg-700 bg-bg-900 overflow-hidden">
      <div className="px-4 py-3 border-b border-bg-700 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-200">Retrieved Knowledge</h2>
        <span className="text-[11px] text-slate-500">{sources.length} sources</span>
      </div>

      <ul className="divide-y divide-bg-800">
        {sources.map((src, idx) => (
          <li key={`${src.source_file}-${src.section}-${idx}`}>
            <button
              onClick={() => onOpen(src.source_file)}
              className="w-full text-left px-4 py-3 hover:bg-bg-850 transition-colors group"
              title={`Open ${src.source_file}`}
            >
              <div className="flex items-center justify-between gap-2 mb-1">
                <span
                  className={`font-mono text-[13px] group-hover:text-accent-400 transition-colors ${
                    idx === 0 ? "text-cyan-300" : "text-slate-200"
                  }`}
                >
                  📄 {src.source_file}
                </span>
                <span className={`text-[11px] font-medium ${RELEVANCE_STYLES[src.relevance]}`}>
                  {src.relevance}
                </span>
              </div>
              <div className="flex items-center gap-2 text-[11px] text-slate-500">
                <span className="px-1.5 py-0.5 rounded bg-bg-800 border border-bg-700">
                  {src.section}
                </span>
                <span>similarity {src.similarity.toFixed(3)}</span>
                <span className="ml-auto text-accent-500 opacity-0 group-hover:opacity-100 transition-opacity">
                  open →
                </span>
              </div>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}