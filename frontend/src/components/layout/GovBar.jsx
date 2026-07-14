export default function GovBar() {
  return (
    <div
      style={{
        background: "#1A3A6B",
        color: "#94A3B8",
        fontSize: 11,
        padding: "4px 20px",
        display: "flex",
        gap: 8,
        alignItems: "center",
      }}
    >
      <span style={{ color: "#C49A1A", fontWeight: 700 }}>भारत सरकार</span>
      <span style={{ color: "#334155" }}>|</span>
      <span>Government of India</span>
      <span style={{ marginLeft: "auto", color: "#475569" }}>
        National Informatics Centre · NITI Aayog
      </span>
    </div>
  );
}
