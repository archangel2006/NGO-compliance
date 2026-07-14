export default function Card({ children, s }) {
  return (
    <div
      style={{
        background: "#FFFFFF",
        borderRadius: 10,
        border: "1px solid #E2E8F0",
        padding: 20,
        ...s,
      }}
    >
      {children}
    </div>
  );
}
