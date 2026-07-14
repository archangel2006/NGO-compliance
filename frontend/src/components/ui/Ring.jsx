export default function Ring({ score }) {
  const radius = 48;
  const circumference = 2 * Math.PI * radius;
  const dash = (score / 100) * circumference;
  const color = score >= 80 ? "#16A34A" : score >= 60 ? "#D97706" : "#DC2626";

  return (
    <div style={{ position: "relative", width: 120, height: 120, flexShrink: 0 }}>
      <svg
        viewBox="0 0 120 120"
        style={{ transform: "rotate(-90deg)", position: "absolute", top: 0, left: 0 }}
      >
        <circle cx="60" cy="60" r={radius} fill="none" stroke="#E2E8F0" strokeWidth="9" />
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="9"
          strokeDasharray={`${dash} ${circumference - dash}`}
          strokeLinecap="round"
        />
      </svg>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <span style={{ fontSize: 26, fontWeight: 900, color, lineHeight: 1 }}>{score}</span>
        <span
          style={{
            fontSize: 9,
            color,
            fontWeight: 700,
            textTransform: "uppercase",
            marginTop: 2,
          }}
        >
          At Risk
        </span>
      </div>
    </div>
  );
}
