import apiClient from "../lib/apiClient";

export const fetchVaultOverview = () => apiClient.get("/vault");

export const downloadVaultFile = (fileId) =>
  apiClient.get(`/vault/files/${fileId}/download`, {
    responseType: "blob",
  });

export const deleteVaultFile = (fileId) => apiClient.delete(`/vault/files/${fileId}`);
