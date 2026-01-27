import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGoogleLogin } from "@react-oauth/google";
import "./styles/Login.css";
import { useAuth } from "../context/AuthContext.jsx";
import { fetchGoogleProfile } from "../utils/googleProfile.js";

const Login = () => {
  const navigate = useNavigate();
  const { login, googleLogin, isSubmitting } = useAuth();
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [feedback, setFeedback] = useState(null);

  const handleFieldChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setFeedback(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFeedback(null);
    try {
      await login(formData);
      setFeedback({ type: "success", message: "Login successful." });
    } catch (error) {
      setFeedback({ type: "error", message: error.message || "Login failed." });
    }
  };

  const handleGoogleSuccess = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        const profile = await fetchGoogleProfile(tokenResponse.access_token);
        await googleLogin({
          email: profile.email,
          username: profile.given_name || profile.name || profile.email,
          googleId: profile.sub,
        });
        setFeedback({ type: "success", message: "Signed in with Google." });
      } catch (error) {
        setFeedback({
          type: "error",
          message: error.message || "Unable to sign in with Google.",
        });
      }
    },
    onError: () =>
      setFeedback({
        type: "error",
        message: "Google sign-in was cancelled. Please try again.",
      }),
    scope: "profile email",
  });

  return (
    <div className="login-container">
      
      {/* LEFT SIDE: Visual Anchor */}
      <div className="brand-panel">
        <h1 className="brand-title">labmate.ai</h1>
        <p className="brand-desc">
          Next-generation clinical analysis powered by artificial intelligence. 
          Secure, fast, and precise.
        </p>
      </div>

      {/* RIGHT SIDE: Interactive Form */}
      <div className="form-panel">
        <div className="auth-card">
          
          <div className="header-text">
            <h2>Welcome back</h2>
            <p>Enter your credentials to access the lab.</p>
          </div>

          <form onSubmit={handleSubmit} autoComplete="off">
            
            {/* Email Field */}
            <div className="input-group">
              <input
                type="email"
                name="email"
                placeholder=" "
                required
                autoComplete="off"
                value={formData.email}
                onChange={handleFieldChange}
              />
              <label>Email Address</label>
            </div>

            {/* Password Field */}
            <div className="input-group">
              <input
                type="password"
                name="password"
                placeholder=" "
                required
                autoComplete="new-password"
                value={formData.password}
                onChange={handleFieldChange}
              />
              <label>Password</label>
            </div>

            <button type="submit" className="btn-primary" disabled={isSubmitting}>
              Sign In
            </button>
          </form>

          <div className="divider">
            <span>OR</span>
          </div>

          {/* Google Button */}
          <button
            type="button"
            className="btn-google"
            onClick={() => handleGoogleSuccess()}
            disabled={isSubmitting}
          >
            <img 
              src="https://www.svgrepo.com/show/475656/google-color.svg" 
              alt="Google" 
              style={{ width: "20px", height: "20px" }} 
            />
            Sign in with Google
          </button>

          {/* Toggle Login/Signup */}
          <p className="switch-text">
            Don't have an account?
            <button
              type="button"
              className="switch-link"
              onClick={() => navigate("/signup")}
            >
              Sign up
            </button>
          </p>

          {feedback?.message && (
            <div className={`auth-feedback ${feedback.type}`}>
              {feedback.message}
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default Login;