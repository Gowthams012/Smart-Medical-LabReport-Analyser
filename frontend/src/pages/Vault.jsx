import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { fetchVaultOverview, downloadVaultFile } from "../services/vaultService";
import "./styles/Vault.css";

const formatBytes = (value = 0) => {
  if (!value || Number.isNaN(value)) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(value) / Math.log(1024)), units.length - 1);
  const size = value / Math.pow(1024, index);
  return `${size.toFixed(size >= 10 ? 0 : 1)} ${units[index]}`;
};

const formatDate = (value) => {
  if (!value) return "Unknown";
  return new Date(value).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};

const Vault = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [patientVaults, setPatientVaults] = useState([]);
  const [stats, setStats] = useState({ totalPatients: 0, totalReports: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedGroup, setExpandedGroup] = useState(null);

  const initials = useMemo(
    () =>
      (user?.username || user?.email || "LM")
        .split(" ")
        .map((word) => word[0])
        .join("")
        .slice(0, 2)
        .toUpperCase(),
    [user]
  );

  const handleNavigate = (path) => () => navigate(path);
  const isActive = (path) => location.pathname === path;

  const loadVault = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const {
        data: { data = {} },
      } = await fetchVaultOverview();
      setPatientVaults(data.patientVaults || []);
      setStats({
        totalPatients: data.stats?.totalPatients ?? (data.patientVaults || []).length,
        totalReports: data.stats?.totalReports ?? (data.patientVaults || []).reduce((sum, item) => sum + (item.totalFiles || 0), 0),
      });
    } catch (err) {
      const message = err.response?.data?.message || "Unable to load vault";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadVault();
  }, [loadVault]);

  const handleDownload = async (file) => {
    try {
      const response = await downloadVaultFile(file.id);
      const blob = new Blob([response.data], { type: file.fileType || "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = file.fileName || "lab-report.pdf";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      const message = err.response?.data?.message || "Unable to download file";
      setError(message);
    }
  };

  const toggleGroup = (key) => {
    setExpandedGroup((prev) => (prev === key ? null : key));
  };

  const renderFiles = (patient, index) => {
    const groupKey = `${patient.patientName}-${patient.vaultPath || index}`;
    const isExpanded = expandedGroup === groupKey;
    const files = isExpanded ? patient.files : patient.files?.slice(0, 3) || [];

    return (
      <>
        <div className="vault-file-list">
          {files.map((file) => (
            <div className="vault-file-row" key={file.id}>
              <div className="vault-file-info">
                <p className="vault-file-name" title={file.fileName}>{file.fileName}</p>
                <span className="vault-file-meta">
                  {formatDate(file.uploadDate)} • {formatBytes(file.fileSize)}
                </span>
              </div>
              <div className="vault-file-actions">
                <span className={`status-pill status-${file.status}`}>{file.status}</span>
                <button type="button" onClick={() => handleDownload(file)}>
                  Download
                </button>
              </div>
            </div>
          ))}
        </div>
        {patient.totalFiles > 3 && (
          <button type="button" className="vault-expand" onClick={() => toggleGroup(groupKey)}>
            {isExpanded ? "Show fewer files" : `View all ${patient.totalFiles} files`}
          </button>
        )}
      </>
    );
  };

  return (
    <div className="vault-page">
      <header className="navbar">
        <button type="button" className="nav-brand" onClick={handleNavigate("/home")}>
          <div className="logo-icon">LM</div>
          <span className="brand-text">
            labmate<span>.ai</span>
          </span>
        </button>

        <ul className="nav-links">
          <li className={`nav-item ${isActive("/home") ? "active" : ""}`} onClick={handleNavigate("/home")}>
            Home
          </li>
          <li
            className={`nav-item ${isActive("/chat-history") ? "active" : ""}`}
            onClick={handleNavigate("/chat-history")}
          >
            Chat History
          </li>
          <li className={`nav-item ${isActive("/vaults") ? "active" : ""}`} onClick={handleNavigate("/vaults")}>
            Vaults
          </li>
          <li className={`nav-item ${isActive("/profile") ? "active" : ""}`} onClick={handleNavigate("/profile")}>
            Profile
          </li>
        </ul>

        <button type="button" className="profile-pic" onClick={handleNavigate("/profile")}>
          {initials}
        </button>
      </header>

      <main className="vault-container">
        <section className="vault-hero">
          <div>
            <p className="vault-label">Patient vault</p>
            <h1>Every report, neatly filed</h1>
            <p>
              Each upload is automatically routed into a patient-specific vault. Continue where you left off
              or reopen prior diagnostics without digging through folders manually.
            </p>
          </div>
          <div className="vault-hero-actions">
            <button type="button" className="pill-button" onClick={handleNavigate("/home")}>
              Upload new report
            </button>
            <button type="button" className="outline-btn" onClick={loadVault} disabled={isLoading}>
              {isLoading ? "Refreshing..." : "Refresh"}
            </button>
          </div>
        </section>

        <section className="vault-stats">
          <article className="vault-stat-card">
            <p className="stat-label">Patients organised</p>
            <h2>{stats.totalPatients}</h2>
          </article>
          <article className="vault-stat-card">
            <p className="stat-label">Reports stored</p>
            <h2>{stats.totalReports}</h2>
          </article>
        </section>

        {error && <div className="vault-error">{error}</div>}

        {isLoading ? (
          <div className="vault-loading">Syncing vault records...</div>
        ) : patientVaults.length === 0 ? (
          <div className="vault-empty">
            <h3>No patient folders yet</h3>
            <p>Upload your first report to generate a vault automatically.</p>
            <button type="button" onClick={handleNavigate("/home")}>
              Start with a new report
            </button>
          </div>
        ) : (
          <section className="vault-grid">
            {patientVaults.map((patient, index) => (
              <article className="vault-card" key={`${patient.patientName}-${index}`}>
                
                {/* HEADER: Removed raw path */}
                <div className="vault-card-header">
                  <div className="vault-folder-icon">📁</div>
                  <div className="vault-header-info">
                    <p className="vault-patient-label">Patient folder</p>
                    <h3 title={patient.patientName}>{patient.patientName}</h3>
                  </div>

                  <div className="vault-card-meta">
                    <span>{patient.totalFiles} files</span>
                    <span>{formatDate(patient.lastUpdated)}</span>
                  </div>
                </div>

                {/* BODY: Removed Folder Alias, Kept Total Size */}
                <div className="vault-card-body">
                  <div className="vault-card-summary">
                     <div className="summary-item">
                       <span className="summary-label">Total Size:</span>
                       <span className="summary-value">{formatBytes(patient.totalSize)}</span>
                     </div>
                  </div>

                  {renderFiles(patient, index)}
                </div>

              </article>
            ))}
          </section>
        )}
      </main>
    </div>
  );
};

export default Vault;