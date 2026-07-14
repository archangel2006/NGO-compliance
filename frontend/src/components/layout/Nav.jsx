import { Bell, LogIn } from "lucide-react";

export default function Nav({ go, page }) {
  const links = ["Home", "NPO Directory", "Compliance Check"];
  const pageMap = {
    Home: "landing",
    "NPO Directory": "directory",
    "Compliance Check": "submit",
  };

  return (
    <div
      style={{
        background: "#FFFFFF",
        borderBottom: "3px solid #E8601A",
        padding: "0 20px",
        display: "flex",
        alignItems: "center",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "10px 0",
          marginRight: 28,
          cursor: "pointer",
        }}
        onClick={() => go("landing")}
      >
        <div>
          <div style={{ fontWeight: 800, fontSize: 17, color: "#1A3A6B", letterSpacing: "0.02em" }}>
            NGO Compliance
          </div>
          <div style={{ fontSize: 9, color: "#64748B" }}>Verification System · Pilot</div>
        </div>
      </div>

      <div style={{ display: "flex", flex: 1 }}>
        {links.map((link) => {
          const active =
            (link === "Compliance Check" && ["submit", "processing", "dashboard", "findings", "queue", "report"].includes(page)) ||
            (link === "NPO Directory" && page === "directory") ||
            (link === "Home" && page === "landing");

          return (
            <div
              key={link}
              onClick={() => (pageMap[link] ? go(pageMap[link]) : undefined)}
              style={{
                padding: "14px 12px",
                fontSize: 12,
                cursor: pageMap[link] ? "pointer" : "default",
                color: active ? "#E8601A" : "#1A3A6B",
                borderBottom: active ? "3px solid #E8601A" : "3px solid transparent",
                fontWeight: active ? 700 : 400,
                whiteSpace: "nowrap",
              }}
            >
              {link}
            </div>
          );
        })}
      </div>

      <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
        <div style={{ position: "relative", cursor: "pointer", padding: 6 }}>
          <Bell size={16} style={{ color: "#64748B" }} />
          <span
            style={{
              position: "absolute",
              top: 3,
              right: 3,
              width: 7,
              height: 7,
              borderRadius: "50%",
              background: "#DC2626",
            }}
          />
        </div>
        <button
          onClick={() => go("landing")}
          style={{
            background: "#E8601A",
            color: "#FFFFFF",
            border: "none",
            borderRadius: 6,
            padding: "7px 14px",
            fontWeight: 600,
            fontSize: 12,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: 5,
          }}
        >
          <LogIn size={13} />Login / Signup
        </button>
      </div>
    </div>
  );
}
