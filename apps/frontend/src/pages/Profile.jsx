import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import "./styles/Profile.css";

const Profile = () => {
  const { user, logout, isSubmitting } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Generate Initials safely
  const initials = (user?.username || user?.email || "LM")
    .split(" ")
    .map((word) => word[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  const handleNavigate = (path) => () => navigate(path);
  const isActive = (path) => location.pathname === path;

  return (
    <div className="profile-page">
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

      <div className="profile-container">
        <div className="profile-card">
          <div className="profile-avatar">{initials}</div>
          <h1 className="profile-name">{user?.username || "LabMate User"}</h1>
          <p className="profile-email">{user?.email || "user@example.com"}</p>

          <button
            type="button"
            className="logout-btn"
            onClick={handleLogout}
            disabled={isSubmitting}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            {isSubmitting ? "Signing out..." : "Sign Out"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;