import apiClient from "../lib/apiClient";

export const uploadReport = (file) => {
  const formData = new FormData();
  formData.append("pdfFile", file);

  return apiClient.post("/extraction/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const fetchReportById = (reportId) =>
  apiClient.get(`/extraction/reports/${reportId}`);

export const fetchReports = () => apiClient.get("/extraction/reports");
