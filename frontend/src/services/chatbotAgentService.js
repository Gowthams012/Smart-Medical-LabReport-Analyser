import apiClient from "../lib/apiClient";

export const askChatbotAgent = ({ chatId, message }) =>
  apiClient.post("/chat/message", { chatId, message });
