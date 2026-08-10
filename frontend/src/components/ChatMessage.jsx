import SourceList from "./SourceList.jsx";

export default function ChatMessage({ role, text, sources }) {
  const label = role === "user" ? "You" : "AI";

  return (
    <div className={`chat-message ${role}`}>
      <p>
        <strong>{label}:</strong> {text}
      </p>
      <SourceList sources={sources} />
    </div>
  );
}
