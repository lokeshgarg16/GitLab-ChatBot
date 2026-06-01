import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
});

export async function fetchChat(query, sessionId = "user123") {
  try {
    const response = await apiClient.post("/chat/", {
      query,
      session_id: sessionId,
    });

    console.log("Chat API response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Chat API error:", error.response?.data || error.message);
    throw error;
  }
}

export async function uploadDocument(file) {
  try {
    const form = new FormData();
    form.append("file", file);

    const response = await apiClient.post("/upload/", form, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      timeout: 180000,
    });

    console.log("Upload API response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Upload API error:", error.response?.data || error.message);
    throw error;
  }
}

export async function getUploadedDocuments() {
  try {
    const response = await apiClient.get("/upload/");
    return response.data;
  } catch (error) {
    console.error(
      "List uploaded docs error:",
      error.response?.data || error.message
    );
    throw error;
  }
}

export async function deleteUploadedDocument(source) {
  try {
    const encodedSource = encodeURIComponent(source);

    const response = await apiClient.delete(`/upload/${encodedSource}`);
    return response.data;
  } catch (error) {
    console.error(
      "Delete uploaded doc error:",
      error.response?.data || error.message
    );
    throw error;
  }
}

export const listUploadedDocs = getUploadedDocuments;
export const deleteUploadedDoc = deleteUploadedDocument;