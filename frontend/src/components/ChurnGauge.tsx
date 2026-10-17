const MAX = 50;

export default function ChurnGauge({ value }: { value: number }) {
  const ratio = Math.min(value, MAX) / MAX;
  const angle = Math.PI * (1 - ratio);
  const r = 80;
  const cx = 100;
  const cy = 100;
  const end = { x: cx + r * Math.cos(angle), y: cy - r * Math.sin(angle) };
  const color = value < 5 ? "#10b981" : value < 15 ? "#f59e0b" : "#ef4444";
  const verdict = value < 5 ? "Low risk" : value < 15 ? "Watch closely" : "High churn risk";

  return (
    <div className="gauge">
      <svg viewBox="0 0 200 120" role="img" aria-label={`Churn rate ${value}%`}>
        <path d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`} stroke="#2a3245" strokeWidth="16" fill="none" strokeLinecap="round" />
        {ratio > 0 && (
          <path d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${end.x} ${end.y}`} stroke={color} strokeWidth="16" fill="none" strokeLinecap="round" />
        )}
        <text x={cx} y={cy - 12} textAnchor="middle" fill="#f1f5f9" fontSize="28" fontWeight="700">{value.toFixed(1)}%</text>
        <text x={cx - r} y={cy + 18} textAnchor="middle" fill="#64748b" fontSize="10">0%</text>
        <text x={cx + r} y={cy + 18} textAnchor="middle" fill="#64748b" fontSize="10">{MAX}%+</text>
      </svg>
      <strong style={{ color }}>{verdict}</strong>
      <span className="muted">Share of shoppers who would leave without buying</span>
    </div>
  );
}
