import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import "./index.css";
import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";

const googleClientId =
  import.meta.env.VITE_GOOGLE_CLIENT_ID || "missing-google-client-id";

if (googleClientId === "missing-google-client-id") {
  console.warn(
    "VITE_GOOGLE_CLIENT_ID is missing. Google authentication will fail until it is configured."
  );
}

const AppProviders = () => (
  <GoogleOAuthProvider clientId={googleClientId}>
    <AuthProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </AuthProvider>
  </GoogleOAuthProvider>
);

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AppProviders />
  </React.StrictMode>
);
