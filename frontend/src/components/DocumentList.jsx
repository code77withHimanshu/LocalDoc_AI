import { useState } from "react";

export default function DocumentList({ documents, onDelete }) {
  const [deletingName, setDeletingName] = useState(null);

  async function handleRemove(name) {
    setDeletingName(name);
    try {
      await onDelete(name);
    } finally {
      setDeletingName(null);
    }
  }

  return (
    <div className="panel">
      <h2>Documents</h2>
      {documents.length === 0 ? (
        <p className="muted">No documents uploaded yet.</p>
      ) : (
        <ul className="document-list">
          {documents.map((name) => (
            <li key={name}>
              <span>{name}</span>
              <button
                className="remove-button"
                onClick={() => handleRemove(name)}
                disabled={deletingName === name}
              >
                {deletingName === name ? "Removing..." : "Remove"}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
