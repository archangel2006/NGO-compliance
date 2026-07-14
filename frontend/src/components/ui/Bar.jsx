export default function Bar({ v }) {
  const progress = Math.round(v * 100);
  const color = progress >= 85 ? "#16A34A" : progress >= 70 ? "#D97706" : "#DC2626";

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ flex: 1, background: "#E2E8F0", borderRadius: 4, height: 5 }}>
        <div
          style={{
            width: `${progress}%`,
            height: 5,
            borderRadius: 4,
            background: color,
          }}
        />
      </div>
      <span style={{ fontSize: 11, color, fontWeight: 600, minWidth: 28 }}>
        {progress}%
      </span>
    </div>
  );
}
