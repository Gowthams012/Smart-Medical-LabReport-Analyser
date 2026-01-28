// src/app.js
// -------------------------------------
// Main Express app configuration
// -------------------------------------

const express = require("express");
const cors = require("cors");

const app = express();

// Enable CORS for frontend communication
app.use(cors());

// Parse incoming JSON requests with larger limit
app.use(express.json({ limit: '10mb' }));

// Parse URL encoded data
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Routes
app.use("/api/auth", require("./routes/authRoutes"));
app.use("/api/extraction", require("./routes/extractionRoutes"));
app.use("/api/chat", require("./routes/chatbotRoutes"));
app.use("/api/vault", require("./routes/vaultRoutes"));

// Health check route
app.get("/", (req, res) => {
  res.send("✅ Smart Medical Lab Report Analyzer API Running");
});

module.exports = app;
