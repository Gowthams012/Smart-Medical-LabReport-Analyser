import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { listChatSessions } from "../services/chatService";
import { useAuth } from "../context/AuthContext.jsx";
import "./styles/ChatHistory.css";

const formatDateTime = (value) => {
	if (!value) return "Unknown";
	return new Date(value).toLocaleString(undefined, {
		month: "short",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
	});
};

const ChatHistory = () => {
	const { user } = useAuth();
	const navigate = useNavigate();
	const location = useLocation();
	const [sessions, setSessions] = useState([]);
	const [isLoading, setIsLoading] = useState(true);
	const [error, setError] = useState(null);

	const handleNavigate = (path) => () => navigate(path);
	const isActive = (path) => location.pathname === path;

	useEffect(() => {
		const fetchSessions = async () => {
			setIsLoading(true);
			setError(null);
			try {
				const {
					data: { data = [] },
				} = await listChatSessions();
				setSessions(data);
			} catch (err) {
				const message = err.response?.data?.message || "Unable to load chat history.";
				setError(message);
			} finally {
				setIsLoading(false);
			}
		};

		fetchSessions();
	}, []);

	const handleOpenChat = (session) => {
		navigate(`/chat/${session.chatId}`, {
			state: {
				reportId: session.report?._id,
				patientName: session.report?.patientName,
			},
		});
	};

	const handleNavigateToChat = () => {
		if (sessions.length > 0) {
			handleOpenChat(sessions[0]);
			return;
		}
		navigate("/home");
	};

	return (
		<div className="chat-history-page">
			<header className="navbar">
				<button className="nav-brand" onClick={() => navigate("/home")}>
					<div className="logo-icon">LM</div>
					<span className="brand-text">
						labmate<span>.ai</span>
					</span>
				</button>

				<ul className="nav-links">
					<li className={`nav-item ${isActive("/home") ? "active" : ""}`} onClick={handleNavigate("/home")}>
						Home
					</li>
					<li className={`nav-item ${isActive("/chat-history") ? "active" : ""}`} onClick={handleNavigate("/chat-history")}>
						Chat History
					</li>
					<li className="nav-item" onClick={handleNavigateToChat}>Chat</li>
					<li className={`nav-item ${isActive("/vaults") ? "active" : ""}`} onClick={handleNavigate("/vaults")}>
						Vaults
					</li>
					<li className={`nav-item ${isActive("/profile") ? "active" : ""}`} onClick={handleNavigate("/profile")}>
						Profile
					</li>
				</ul>

				<div className="profile-pill">
					{(user?.username || user?.email || "ME").slice(0, 2).toUpperCase()}
				</div>
			</header>

			<main className="chat-history-container">
				<div className="history-header">
					<div>
						<p className="history-label">Saved conversations</p>
						<h1>Your chat history</h1>
						<p className="history-subtext">
							Revisit prior consultations to continue where you left off.
						</p>
					</div>
					<button className="pill-button" onClick={() => navigate("/home")}>
						Upload new report
					</button>
				</div>

				{error && <div className="history-error">{error}</div>}

				{isLoading ? (
					<div className="history-loading">Loading conversations...</div>
				) : sessions.length === 0 ? (
					<div className="history-empty">
						<p>No chat sessions yet.</p>
						<button type="button" onClick={() => navigate("/home")}>
							Start your first analysis
						</button>
					</div>
				) : (
					<div className="history-grid">
						{sessions.map((session) => (
							<article key={session.chatId} className="history-card">
								<div className="history-card-header">
									<h3>{session.report?.patientName || "Unknown patient"}</h3>
									<span className={`status-badge ${session.messageCount ? "completed" : "pending"}`}>
										{session.messageCount ? `${session.messageCount} messages` : "No messages"}
									</span>
								</div>

								<p className="history-meta">
									{session.report?.reportType || "Lab Report"} • Updated {formatDateTime(session.updatedAt)}
								</p>

								{session.lastMessage?.message && (
									<p className="history-snippet">{session.lastMessage.message.substring(0, 180)}...</p>
								)}

								<div className="history-actions">
									<button type="button" className="outline-btn" onClick={() => handleOpenChat(session)}>
										Continue chat
									</button>
								</div>
							</article>
						))}
					</div>
				)}
			</main>
		</div>
	);
};

export default ChatHistory;
