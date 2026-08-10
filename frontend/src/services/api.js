import axios from "axios";

// The React app only ever talks to the Spring Boot backend, never
// directly to the Python AI service.
const api = axios.create({
  baseURL: "http://localhost:8080/api",
});

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/documents", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function fetchDocuments() {
  const response = await api.get("/documents");
  return response.data.documents;
}

export async function deleteDocument(filename) {
  await api.delete(`/documents/${encodeURIComponent(filename)}`);
}

export async function askQuestion(question) {
  const response = await api.post("/chat", { question });
  return response.data;
}
