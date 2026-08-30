import { LANGUAGES } from "../services/api.js";

export default function InputPanel({
  value,
  onValueChange,
  language,
  onLanguageChange,
  onAnalyze,
  onClear,
  onExample,
  loading,
  exampleIndex,
}) {
  return (
    <section className="rounded-xl border border-bg-700 bg-bg-900 overflow-hidden">
      <div className="px-4 py-3 border-b border-bg-700 flex items-center justify-between">
        <label htmlFor="error-input" className="text-sm font-semibold text-slate-200">
          Paste your error or stack trace
        </label>
        <span className="text-[11px] text-slate-500 font-mono">input</span>
      </div>

      <textarea
        id="error-input"
        value={value}
        onChange={(e) => onValueChange(e.target.value)}
        placeholder={
          'e.g.\n\njava.lang.NullPointerException: Cannot invoke "User.getName()" because "user" is null\n\tat UserService.java:42'
        }
        spellCheck={false}
        className="w-full h-48 sm:h-56 bg-bg-900 px-4 py-3 font-mono text-[13px] text-slate-200 placeholder:text-slate-600 outline-none resize-y focus:bg-bg-850 transition-colors"
      />

      <div className="px-4 py-3 border-t border-bg-700 flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <span className="block text-[11px] uppercase tracking-wider text-slate-500 mb-1.5">
            Language
          </span>
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
            className="w-full sm:w-48 bg-bg-800 border border-bg-700 rounded-lg px-3 py-2 text-sm text-slate-200 outline-none focus:border-accent-500 cursor-pointer"
          >
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col sm:flex-row gap-2 sm:items-end mt-3 sm:mt-0">
          <button
            type="button"
            onClick={onExample}
            className="px-4 py-2 rounded-lg border border-bg-700 bg-bg-800 text-sm text-slate-300 hover:border-accent-500/50 hover:text-accent-400 transition-colors"
            title="Load a built-in example"
          >
            Try Example {exampleIndex >= 0 ? `(${exampleIndex + 1})` : ""}
          </button>
          <button
            type="button"
            onClick={onClear}
            className="px-4 py-2 rounded-lg border border-bg-700 bg-bg-800 text-sm text-slate-300 hover:border-danger/50 hover:text-danger transition-colors"
            title="Clear input"
          >
            Clear
          </button>
          <button
            type="button"
            onClick={onAnalyze}
            disabled={loading || !value.trim()}
            className="px-6 py-2 rounded-lg bg-accent-600 hover:bg-accent-500 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-semibold text-white shadow-glow transition-colors inline-flex items-center gap-2"
          >
            {loading ? (
              <>
                <Spinner />
                Analyzing…
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path
                    d="M5 12h14M13 6l6 6-6 6"
                    stroke="currentColor"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                Analyze Error
              </>
            )}
          </button>
        </div>
      </div>
    </section>
  );
}

function Spinner() {
  return (
    <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeOpacity="0.25" strokeWidth="3" />
      <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}