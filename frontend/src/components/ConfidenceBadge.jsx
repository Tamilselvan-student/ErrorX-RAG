const STYLES = {
  High: "text-success border-success/40 bg-success/10",
  Medium: "text-warn border-warn/40 bg-warn/10",
  Low: "text-danger border-danger/40 bg-danger/10",
};

const DOT = {
  High: "bg-success",
  Medium: "bg-warn",
  Low: "bg-danger",
};

export default function ConfidenceBadge({ level, reason, small = false }) {
  const cls = STYLES[level] || STYLES.Low;
  return (
    <span
      title={reason || `Confidence: ${level}`}
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${cls} ${
        small ? "px-2 py-0.5 text-[11px]" : "px-3 py-1 text-sm"
      }`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${DOT[level] || "bg-danger"}`} />
      {level} confidence
    </span>
  );
}