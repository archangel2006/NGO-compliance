import { ChevronRight } from "lucide-react";

export default function Crumb({ items, go }) {
  return (
    <div style={{ background: "#FFFFFF", borderBottom: "1px solid #E2E8F0", padding: "10px 20px" }}>
      <div
        style={{
          maxWidth: 1040,
          margin: "0 auto",
          display: "flex",
          alignItems: "center",
          gap: 4,
          fontSize: 12,
          color: "#64748B",
          flexWrap: "wrap",
        }}
      >
        {items.map((item, index) => (
          <span key={`${item.label}-${index}`} style={{ display: "flex", alignItems: "center", gap: 4 }}>
            {index > 0 && <ChevronRight size={11} />}
            <span
              style={{
                color: item.page ? "#E8601A" : "#1A3A6B",
                fontWeight: item.page ? 400 : 600,
                cursor: item.page ? "pointer" : "default",
              }}
              onClick={item.page ? () => go(item.page) : undefined}
            >
              {item.label}
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}
