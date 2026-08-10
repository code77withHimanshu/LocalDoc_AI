import { useState } from "react";
import { uploadDocument } from "../services/api.js";

export default function DocumentUpload({ onUploaded, onError }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  async function handleUpload() {
    if (!file) {
      onError("Please choose a file first");
      return;
    }
    setUploading(true);
    try {
      await uploadDocument(file);
      setFile(null);
      onUploaded();
    } catch (err) {
      onError(err.response?.data?.error || "Failed to upload document");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="panel">
      <h2>Upload Document</h2>
      <div className="upload-row">
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={(e) => setFile(e.target.files[0] || null)}
        />
        <button onClick={handleUpload} disabled={uploading}>
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </div>
    </div>
  );
}
