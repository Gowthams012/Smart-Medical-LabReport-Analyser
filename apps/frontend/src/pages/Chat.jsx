import React, { useState, useRef, useEffect } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { fetchChatHistory } from "../services/chatService";
import { fetchReportById } from "../services/reportService";
import { askChatbotAgent } from "../services/chatbotAgentService";
import "./styles/Chat.css";

const SECTION_HEADINGS = [
  "LAB-AWARE OPENING",
  "RISK INSIGHT",
  "FOOD & LIFESTYLE BOOST",
  "SAFETY REMINDER",
  "RECOMMENDED ACTIONS",
  "RECOMMENDED NEXT STEPS",
  "IMPORTANT NOTE",
  "SUMMARY",
];

const simplifyAssistantText = (text = "") => {
  if (!text) return "";

  const cleaned = text
    .replace(/\*\*/g, "")
    .replace(/[_`]/g, "")
    .replace(/={3,}/g, "")
    .replace(/Insight Agent - Lab Report Analysis/gi, "")
    .replace(/Source File:.*$/gim, "")
    .replace(/Generated:.*$/gim, "");

  const lines = cleaned
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length)
    .filter((line) => !SECTION_HEADINGS.includes(line.toUpperCase()));

  const normalized = lines.map((line) => line.replace(/^[-*•\d\.]+\s*/, () => "• "));

  if (!normalized.length) {
    return text.trim();
  }

  const MAX_LINES = 8;
  const concise = normalized.slice(0, MAX_LINES);
  if (normalized.length > MAX_LINES) {
    concise.push("• For more details, ask about a specific test or symptom.");
  }

  return concise.join("\n");
};

// --- HELPER: Universal Text Formatter ---
// Converts raw text, lists, and headers into interactive UI elements
const FormattedText = ({ text }) => {
  if (!text) return null;

  // 1. Filter out System/Technical Logs
  const cleanLines = text
    .split(/\r?\n/)
    .filter(line => 
      !line.match(/^Source File:/i) &&
      !line.match(/^Generated:/i) &&
      !line.match(/^=+.*=+$/) && 
      !line.match(/^Insight Agent -/i) &&
      line.trim().length > 0
    );

  return (
    <div className="formatted-content">
      {cleanLines.map((line, index) => {
        let content = line.trim();

        // 2. HEADERS: Remove ### and Make Bold
        if (content.startsWith("#")) {
          const cleanHeader = content.replace(/^#+\s*/, "").replace(/\*\*/g, "");
          return <h4 key={index}>{cleanHeader}</h4>;
        }

        // 3. INTERACTIVE LISTS: Detects Bullets (-, *, •) AND Numbers (1., 2.)
        if (content.match(/^[-*•]\s/) || content.match(/^\d+\.\s/)) {
          // Remove the symbol/number to get clean text
          const cleanItem = content.replace(/^([-*•]|\d+\.)\s/, "").replace(/\*\*/g, "");
          return (
            <div key={index} className="interactive-point">
              <span className="dot"></span>
              <span>{cleanItem}</span>
            </div>
          );
        }

        // 4. PARAGRAPHS: Clean normal text
        const cleanParagraph = content.replace(/\*\*/g, "");
        return <p key={index}>{cleanParagraph}</p>;
      })}
    </div>
  );
};

// --- DATA HELPERS ---
function normalizeRecommendations(value) {
  if (!value) return [];
  const rawList = Array.isArray(value) ? value : (typeof value === "string" ? value.split(/\n/) : []);
  
  // Clean up each recommendation string
  return rawList
    .map(item => item.replace(/[*_`#]/g, "").replace(/^\d+\.\s/, "").trim()) 
    .filter(item => item.length > 3);
}

function formatTimestamp(timestamp) {
  if (!timestamp) return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  return new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function formatChatHistory(history = []) {
  return history.map((entry, index) => {
    const sender = entry.role === "user" ? "user" : "ai";
    return {
      id: `${entry.timestamp || index}-${index}`,
      sender,
      text: sender === "ai" ? simplifyAssistantText(entry.message) : entry.message,
      time: formatTimestamp(entry.timestamp),
    };
  });
}

const defaultIntro = {
  id: "intro",
  sender: "ai",
  text: "Hello! I am LabMate. I've analyzed your report. How can I help you?",
  time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
};

const Chat = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { chatId } = useParams();
  const location = useLocation();
  const locationState = location.state || {};
  const messagesEndRef = useRef(null);

  const [messages, setMessages] = useState([defaultIntro]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  const [reportInfo, setReportInfo] = useState({
    patientName: locationState.patientName || user?.username || "Patient",
    summary: locationState.summary || "",
    recommendations: normalizeRecommendations(locationState.recommendations),
  });

  const userInitials = (user?.username || user?.email || "ME").slice(0, 2).toUpperCase();

  // Load Data
  useEffect(() => {
    if (!chatId) return;
    const loadData = async () => {
      setIsLoading(true);
      try {
        const { data: { data } } = await fetchChatHistory(chatId);
        
        const history = formatChatHistory(data.chatHistory || []);
        setMessages(history.length ? history : [defaultIntro]);

        if (data.report) {
          setReportInfo(prev => ({
            ...prev,
            patientName: data.report.patientName || prev.patientName,
            summary: data.report.summary || prev.summary,
            recommendations: normalizeRecommendations(data.report.recommendations) || prev.recommendations
          }));
        }
      } catch (err) {
        console.error("Load Error", err);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, [chatId]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { id: Date.now(), sender: "user", text: input, time: formatTimestamp(new Date()) };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      const { data: { data } } = await askChatbotAgent({ chatId, message: userMsg.text });
      setMessages(formatChatHistory(data.chatHistory));
    } catch (err) {
      setMessages(prev => [...prev, { id: Date.now()+1, sender: "ai", text: "I'm having trouble connecting right now.", time: formatTimestamp(new Date()) }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="chat-page">
      <header className="navbar">
        <button className="nav-brand" onClick={() => navigate("/home")}> 
          <div className="logo-icon">LM</div>
          <span className="brand-text">labmate<span>.ai</span></span>
        </button>
        <ul className="nav-links">
          <li className="nav-item" onClick={() => navigate("/home")}>Home</li>
          <li className="nav-item active">Chat</li>
          <li className="nav-item" onClick={() => navigate("/chat-history")}>Chat History</li>
          <li className="nav-item" onClick={() => navigate("/vaults")}>Vaults</li>
          <li className="nav-item" onClick={() => navigate("/profile")}>Profile</li>
        </ul>
        <div className="profile-pill">{userInitials}</div>
      </header>

      <div className="chat-container">
        
        {/* --- LEFT SIDE: REPORT CONTEXT --- */}
        <aside className="report-overview">
          <div className="report-header">
            <div>
              <p className="report-label">Patient Report</p>
              <h2>{reportInfo.patientName}</h2>
            </div>
            <button className="pill-button" onClick={() => navigate("/home")}>Upload New</button>
          </div>

          <div className="report-grid">
            {/* 1. Summary (Uses FormattedText for safety) */}
            <article className="report-card">
              <h3>Clinical Summary</h3>
              {reportInfo.summary ? (
                <FormattedText text={reportInfo.summary} />
              ) : (
                <p style={{fontStyle: 'italic', color: '#94a3b8'}}>Processing summary...</p>
              )}
            </article>

            {/* 2. Recommendations (Explicitly Mapped to Interactive Points) */}
            {reportInfo.recommendations.length > 0 && (
              <article className="report-card">
                <h3>Recommendations</h3>
                <div className="formatted-content">
                  {reportInfo.recommendations.map((rec, i) => (
                    <div key={i} className="interactive-point">
                      <span className="dot"></span>
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </article>
            )}
          </div>
        </aside>

        {/* --- RIGHT SIDE: CHAT MESSAGES --- */}
        <section className="messages-area">
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.sender}`}>
              <div className="chat-avatar">{msg.sender === "user" ? userInitials : "AI"}</div>
              
              <div className="bubble-wrapper">
                <div className="bubble">
                  {/* AI messages get FormattedText to render lists interactively */}
                  {msg.sender === "ai" ? (
                    <FormattedText text={msg.text} />
                  ) : (
                    msg.text
                  )}
                </div>
                <span className="timestamp">{msg.time}</span>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="message ai">
              <div className="chat-avatar">AI</div>
              <div className="typing"><span>•</span><span>•</span><span>•</span></div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </section>

        {/* INPUT */}
        <div className="input-wrapper">
          <form className="input-bar" onSubmit={handleSend}>
             <button type="button" className="attach-btn">
               <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
             </button>
             <input className="chat-input" placeholder="Ask follow-up questions..." value={input} onChange={e => setInput(e.target.value)} disabled={isLoading} />
             <button type="submit" className="send-btn" disabled={isLoading || !input.trim()}>
               <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
             </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chat;