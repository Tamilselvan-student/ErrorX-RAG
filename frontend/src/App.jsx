import { useEffect, useState } from "react";
import Header from "./components/Header.jsx";
import Workspace from "./pages/Workspace.jsx";
import { health } from "./services/api.js";

export default function App() {
  const [backend, setBackend] = useState({ ok: null, info: null });

  useEffect(() => {
    health()
      .then((info) => setBackend({ ok: true, info }))
      .catch(() => setBackend({ ok: false, info: null }));
  }, []);

  return (
    <div className="min-h-full flex flex-col">
      <Header backend={backend} />
      <main className="flex-1">
        <Workspace />
      </main>
      <footer className="border-t border-bg-800 py-4 text-center text-xs text-slate-500">
        ErrorLens · RAG-powered error diagnosis · knowledge docs in{" "}
        <code className="text-cyan-500 font-mono">backend/data/errors</code>
      </footer>
    </div>
  );
}