// server.js
// -------------------------------
// Entry point of the application
// -------------------------------

const app = require("./app");   // Import express app
const connectDB = require("./Database/databaseConnections");
const dotenv = require("dotenv");

// Load environment variables from .env file
dotenv.config({ path: "./config/.env" });

// Connect to MongoDB
connectDB();

// Server port
const PORT = process.env.PORT || 5000;

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
