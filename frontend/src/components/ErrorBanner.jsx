export default function ErrorBanner({ message, onDismiss }) {
  if (!message) return null;
  return (
    <div
      role="alert"
      className="flex items-start gap-3 px-4 py-3 rounded-lg border border-danger/40 bg-danger/10 text-danger text-sm"
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="mt-0.5 shrink-0">
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
        <path d="M12 8v5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <circle cx="12" cy="16.4" r="1" fill="currentColor" />
      </svg>
      <div className="flex-1 leading-relaxed">{message}</div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-danger/70 hover:text-danger font-bold px-1"
          aria-label="Dismiss"
        >
          ×
        </button>
      )}
    </div>
  );
}