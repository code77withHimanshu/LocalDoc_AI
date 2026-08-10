import { useState } from "react";
import { askQuestion } from "../services/api.js";
import ChatMessage from "./ChatMessage.jsx";

export default function ChatWindow({ hasDocuments, onError }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);

  async function handleSend() {
    if (!question.trim()) {
      onError("Please enter a question");
      return;
    }
    if (!hasDocuments) {
      onError("Upload a document before asking questions");
      return;
    }

    const userMessage = { role: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setAsking(true);

    try {
      const { answer, sources } = await askQuestion(userMessage.text);
      setMessages((prev) => [...prev, { role: "ai", text: answer, sources }]);
    } catch (err) {
      onError(err.response?.data?.error || "Failed to get an answer");
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="panel">
      <h2>Chat</h2>
      <div className="chat-messages">
        {messages.map((message, index) => (
          <ChatMessage key={index} {...message} />
        ))}
      </div>
      <div className="chat-input-row">
        <input
          type="text"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend} disabled={asking}>
          {asking ? "Asking..." : "Send"}
        </button>
      </div>
    </div>
  );
}
