export default function Badge({ s, lg }) {
  const meta = {
    PASS:       { bg: "#DCFCE7", c: "#16A34A", t: "✓ PASS" },
    FAIL:       { bg: "#FEE2E2", c: "#DC2626", t: "✗ FAIL" },
    UNCERTAIN:  { bg: "#FEF3C7", c: "#D97706", t: "? UNCERTAIN" },
    MISSING:    { bg: "#F3F4F6", c: "#6B7280", t: "— MISSING" },
    CORPUS_GAP: { bg: "#EFF6FF", c: "#3B82F6", t: "⚠ CORPUS GAP" },
  };

  const resolved = meta[s] || meta.UNCERTAIN;

  return (
    <span
      style={{
        background: resolved.bg,
        color: resolved.c,
        padding: lg ? "5px 14px" : "3px 10px",
        borderRadius: 20,
        fontSize: lg ? 13 : 11,
        fontWeight: 700,
        whiteSpace: "nowrap",
      }}
    >
      {resolved.t}
    </span>
  );
}
