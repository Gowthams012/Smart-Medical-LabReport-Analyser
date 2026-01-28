import apiClient from "../lib/apiClient";

export const startChat = (reportId) =>
  apiClient.post("/chat/start", { reportId });

export const fetchChatHistory = (chatId) =>
  apiClient.get(`/chat/history/${chatId}`);

export const sendChatMessage = ({ chatId, message }) =>
  apiClient.post("/chat/message", { chatId, message });

export const listChatSessions = () => apiClient.get("/chat/sessions");
