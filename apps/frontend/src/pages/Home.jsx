import React, { useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { uploadReport } from "../services/reportService";
import { startChat } from "../services/chatService";
import "./styles/Home.css";

const buildSeededHistory = (summary, recommendations) => {
  const entries = [];
  const now = new Date().toISOString();

  if (summary) {
    entries.push({
      role: "assistant",
      message: `Here is the report summary:\n${summary}`,
      timestamp: now,
    });
  }

  const formattedRecs = Array.isArray(recommendations)
    ? recommendations
    : typeof recommendations === "string"
      ? recommendations
          .split(/\n|•|-/)
          .map((item) => item.trim())
          .filter(Boolean)
      : [];

  if (formattedRecs.length) {
    entries.push({
      role: "assistant",
      message: `Recommended next steps:\n• ${formattedRecs.join("\n• ")}`,
      timestamp: now,
    });
  }

  return entries;
};

const Home = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const initials = (user?.username || user?.email || "LM")
    .split(" ")
    .map((word) => word[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const handleNavigate = (path) => () => navigate(path);
  const isActive = (path) => location.pathname === path;

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setUploadStatus(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus({ type: "error", message: "Please choose a PDF report first." });
      return;
    }

    setIsUploading(true);
    setUploadStatus({ type: "info", message: "Processing report. This may take a moment..." });

    try {
      const {
        data: {
          data: { reportId, summary, recommendations, patientName },
        },
      } = await uploadReport(selectedFile);

      setUploadStatus({ type: "success", message: "Report processed successfully! Opening chat..." });

      const {
        data: {
          data: { chatId, chatHistory = [] },
        },
      } = await startChat(reportId);

      const seededHistory = buildSeededHistory(summary, recommendations);
      const resolvedHistory = chatHistory.length ? chatHistory : seededHistory;

      navigate(`/chat/${chatId}`, {
        replace: true,
        state: {
          reportId,
          summary,
          recommendations,
          patientName,
          initialChatHistory: resolvedHistory,
        },
      });
    } catch (error) {
      const message = error.response?.data?.message || error.message || "Failed to process report.";
      setUploadStatus({ type: "error", message });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="home-container">
      
      {/* --- HEADER --- */}
      <header className="navbar">
        <button type="button" className="nav-brand" onClick={handleNavigate("/home")}>
          <div className="logo-icon">LM</div>
          <span className="brand-text">labmate<span>.ai</span></span>
        </button>

        <ul className="nav-links">
          <li
            className={`nav-item ${isActive("/home") ? "active" : ""}`}
            onClick={handleNavigate("/home")}
          >
            Home
          </li>
          <li
            className={`nav-item ${isActive("/chat-history") ? "active" : ""}`}
            onClick={handleNavigate("/chat-history")}
          >
            Chat History
          </li>
          <li
            className={`nav-item ${isActive("/vaults") ? "active" : ""}`}
            onClick={handleNavigate("/vaults")}
          >
            Vaults
          </li>
          <li
            className={`nav-item ${isActive("/profile") ? "active" : ""}`}
            onClick={handleNavigate("/profile")}
          >
            Profile
          </li>
        </ul>

        <button type="button" className="profile-pic" onClick={handleNavigate("/profile")}>
          {initials}
        </button>
      </header>

      {/* --- MAIN SECTION --- */}
      <main className="main-content">
        
        {/* Welcome Text */}
        <section className="welcome-section">
          <h1>Welcome back, {user?.username || "Clinician"}</h1>
          <p>
            Your AI-powered laboratory assistant is ready. 
            Upload a clinical report to begin analysis or review your previous cases.
          </p>
        </section>

        {/* Upload Button / Zone */}
        <div className="upload-card">
          <div className="upload-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 16L12 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <path d="M9 11L12 8 15 11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M8 16H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <div style={{textAlign: 'center'}}>
            <h3 style={{fontSize: '1.2rem', marginBottom: '0.5rem'}}>Upload Lab Report</h3>
            <span style={{color: '#94a3b8', fontSize: '0.9rem'}}>Drag & drop or click to browse PDF</span>
          </div>
          <input
            type="file"
            accept="application/pdf"
            ref={fileInputRef}
            className="hidden-input"
            onChange={handleFileChange}
          />

          <div className="upload-actions">
            <button
              type="button"
              className="upload-btn outline"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
            >
              {selectedFile ? "Change PDF" : "Select PDF"}
            </button>
            <button
              type="button"
              className="upload-btn primary"
              onClick={handleUpload}
              disabled={isUploading}
            >
              {isUploading ? "Processing..." : "Process & Chat"}
            </button>
          </div>

          {selectedFile && (
            <p className="upload-file-name">Selected: {selectedFile.name}</p>
          )}

          {uploadStatus && (
            <p className={`upload-status ${uploadStatus.type}`}>{uploadStatus.message}</p>
          )}
        </div>
      </main>
    </div>
  );
};

export default Home;