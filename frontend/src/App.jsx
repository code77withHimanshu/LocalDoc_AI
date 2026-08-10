import { useEffect, useState } from "react";
import ChatWindow from "./components/ChatWindow.jsx";
import DocumentList from "./components/DocumentList.jsx";
import DocumentUpload from "./components/DocumentUpload.jsx";
import { deleteDocument, fetchDocuments } from "./services/api.js";

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState("");

  async function loadDocuments() {
    try {
      setDocuments(await fetchDocuments());
    } catch {
      setError("Could not reach the backend. Is it running?");
    }
  }

  async function handleDelete(name) {
    try {
      await deleteDocument(name);
      await loadDocuments();
    } catch (err) {
      setError(err.response?.data?.error || "Failed to remove document");
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  return (
    <div className="app">
      <h1>LocalDoc AI</h1>

      {error && (
        <div className="error-banner" onClick={() => setError("")}>
          {error}
        </div>
      )}

      <DocumentUpload onUploaded={loadDocuments} onError={setError} />
      <DocumentList documents={documents} onDelete={handleDelete} />
      <ChatWindow hasDocuments={documents.length > 0} onError={setError} />
    </div>
  );
}
