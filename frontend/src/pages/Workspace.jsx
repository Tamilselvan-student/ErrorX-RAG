import { useCallback, useEffect, useRef, useState } from "react";
import { analyze, getExamples } from "../services/api.js";
import ErrorBanner from "../components/ErrorBanner.jsx";
import InputPanel from "../components/InputPanel.jsx";
import ResultPanel from "../components/ResultPanel.jsx";
import SourcesPanel from "../components/SourcesPanel.jsx";
import DocumentModal from "../components/DocumentModal.jsx";

export default function Workspace() {
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState("auto");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const [examples, setExamples] = useState([]);
  const [exampleIndex, setExampleIndex] = useState(-1);
  const [activeDoc, setActiveDoc] = useState(null);
  const resultRef = useRef(null);
  const sourcesRef = useRef(null);

  const scrollToSources = () => {
    sourcesRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  useEffect(() => {
    getExamples()
      .then(setExamples)
      .catch(() => setExamples([]));
  }, []);

  const runAnalyze = useCallback(
    async (text, lang) => {
      const payload = { input: text, language: lang || "auto" };
      setLoading(true);
      setError(null);
      try {
        const res = await analyze(payload);
        setResult(res);
        requestAnimationFrame(() =>
          resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })
        );
      } catch (err) {
        setResult(null);
        setError(friendlyError(err));
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const handleAnalyze = () => {
    if (!input.trim() || loading) return;
    runAnalyze(input, language);
  };

  const handleExample = () => {
    if (examples.length === 0 || loading) return;
    const next = exampleIndex + 1;
    const idx = next >= examples.length ? 0 : next;
    const ex = examples[idx];
    setExampleIndex(idx);
    setInput(ex.input);
    setLanguage(ex.language || "auto");
    runAnalyze(ex.input, ex.language || "auto");
  };

  const handleClear = () => {
    setInput("");
    setResult(null);
    setError(null);
    setExampleIndex(-1);
  };

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 py-6">
      {/* Empty-state hero */}
      {!result && !loading && !error && (
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-slate-100">
            Paste any error, stack trace, or short code snippet.
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            ErrorLens analyzes it, retrieves the most relevant explanations from a{" "}
            <span className="text-cyan-400">local knowledge base</span>, and produces a
            structured diagnosis with cited sources.
          </p>
        </div>
      )}

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_360px] gap-6 mt-4 items-start">
        {/* LEFT: input + result */}
        <div className="space-y-5 min-w-0">
          <InputPanel
            value={input}
            onValueChange={setInput}
            language={language}
            onLanguageChange={setLanguage}
            onAnalyze={handleAnalyze}
            onClear={handleClear}
            onExample={handleExample}
            loading={loading}
            exampleIndex={exampleIndex}
          />

          {loading && (
            <div className="rounded-xl border border-bg-700 bg-bg-900 p-6 flex items-center gap-3 text-sm text-slate-400">
              <svg className="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="9" stroke="currentColor" strokeOpacity="0.2" strokeWidth="3" />
                <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
              </svg>
              Running RAG pipeline… analyzing error → retrieving knowledge → generating diagnosis.
            </div>
          )}

          <div ref={resultRef}>
            {!loading && result && (
              <ResultPanel
                result={result}
                onOpenSource={scrollToSources}
              />
            )}
          </div>
        </div>

        {/* RIGHT: sources panel */}
        <aside ref={sourcesRef} className="lg:sticky lg:top-20 space-y-4">
          {result && result.sources?.length > 0 && (
            <SourcesPanel sources={result.sources} onOpen={setActiveDoc} />
          )}

          {!result && !loading && (
            <div className="rounded-xl border border-dashed border-bg-700 bg-bg-900/50 p-4 text-xs text-slate-500">
              <p className="mb-2 font-semibold text-slate-400">Retrieved Knowledge</p>
              <p>
                Sources from the error knowledge base will appear here after an analysis —
                click any source to read its full document.
              </p>
            </div>
          )}
        </aside>
      </div>

      <DocumentModal filename={activeDoc} onClose={() => setActiveDoc(null)} />
    </div>
  );
}

function friendlyError(err) {
  const msg = err?.message || "Something went wrong.";
  if (err?.status === 503 && /llm/i.test(msg)) {
    return (
      "The LLM is not configured. Add LLM_API_KEY (and optionally LLM_BASE_URL, " +
      "LLM_MODEL) to your .env file and restart the backend. You can still inspect " +
      "retrieval by running a search."
    );
  }
  if (err?.status === 502) {
    return "The LLM request failed. Check your LLM_BASE_URL / LLM_MODEL configuration and network.";
  }
  if (err?.status === 503) {
    return msg + " The knowledge base may need re-indexing via POST /api/index.";
  }
  return msg;
}