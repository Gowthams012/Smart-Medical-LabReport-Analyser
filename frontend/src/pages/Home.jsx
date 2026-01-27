import React from "react";
import "./Home.css";

const Home = () => {
  return (
    <div className="home-container">
      
      {/* --- HEADER --- */}
      <header className="navbar">
        <div className="nav-brand">
          <div className="logo-icon">LM</div>
          <span className="brand-text">labmate<span>.ai</span></span>
        </div>

        <ul className="nav-links">
          <li className="nav-item active">Home</li>
          <li className="nav-item">Chat History</li>
          <li className="nav-item">Vaults</li>
          <li className="nav-item">Profiles</li>
        </ul>

        <div className="profile-pic">JD</div>
      </header>

      {/* --- MAIN SECTION --- */}
      <main className="main-content">
        
        {/* Welcome Text */}
        <section className="welcome-section">
          <h1>Welcome, Dr. John</h1>
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
            <span style={{color: '#94a3b8', fontSize: '0.9rem'}}>Drag & drop or click to browse (PDF, JPG)</span>
          </div>
          <button className="upload-btn">Select File</button>
        </div>

        {/* Recent Chat History */}
        <section className="history-section">
          <div className="section-title">Recent Activity</div>

          {/* Item 1 */}
          <div className="chat-item">
            <div className="chat-info">
              <div className="file-icon">📄</div>
              <div>
                <span className="chat-name">Blood_Count_Analysis_v2.pdf</span>
                <span className="chat-date">Last analyzed: Today, 10:30 AM</span>
              </div>
            </div>
            <span className="status-badge completed">Completed</span>
          </div>

          {/* Item 2 */}
          <div className="chat-item">
            <div className="chat-info">
              <div className="file-icon">🔬</div>
              <div>
                <span className="chat-name">MRI_Spine_Scan_004.jpg</span>
                <span className="chat-date">Last analyzed: Yesterday</span>
              </div>
            </div>
            <span className="status-badge pending">Processing</span>
          </div>

        </section>

      </main>
    </div>
  );
};

export default Home;