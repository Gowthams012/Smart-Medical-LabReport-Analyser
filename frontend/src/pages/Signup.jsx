import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGoogleLogin } from "@react-oauth/google";
import "./styles/Login.css";
import { useAuth } from "../context/AuthContext.jsx";
import { fetchGoogleProfile } from "../utils/googleProfile.js";

const Signup = () => {
  const navigate = useNavigate();
  const { signup, googleLogin, isSubmitting } = useAuth();
  const [formData, setFormData] = useState({ username: "", email: "", password: "" });
  const [feedback, setFeedback] = useState(null);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setFeedback(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFeedback(null);
    try {
      await signup({
        username: formData.username,
        email: formData.email,
        password: formData.password,
      });
      setFeedback({ type: "success", message: "Account created successfully." });
      navigate("/login", { replace: true });
    } catch (error) {
      setFeedback({ type: "error", message: error.message || "Signup failed." });
    }
  };

  const handleGoogleSignup = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        const profile = await fetchGoogleProfile(tokenResponse.access_token);
        await googleLogin({
          email: profile.email,
          username: profile.given_name || profile.name || profile.email,
          googleId: profile.sub,
        });
        setFeedback({
          type: "success",
          message: "Signed up with Google successfully.",
        });
        navigate("/login", { replace: true });
      } catch (error) {
        setFeedback({
          type: "error",
          message: error.message || "Unable to sign up with Google.",
        });
      }
    },
    onError: () =>
      setFeedback({
        type: "error",
        message: "Google signup was cancelled. Please try again.",
      }),
    scope: "profile email",
  });

  return (
    <div className="login-container">
      
      {/* --- LEFT SIDE: BRANDING (Consistent with Login) --- */}
      <div className="brand-panel">
        <h1 className="brand-title">labmate.ai</h1>
        <p className="brand-desc">
          Join the next generation of clinical analysis. 
          Create your workspace and start analyzing data with AI precision.
        </p>
      </div>

      {/* --- RIGHT SIDE: SIGNUP FORM --- */ }
      <div className="form-panel">
        <div className="auth-card">
          
          <div className="header-text">
            <h2>Create Account</h2>
            <p>Sign up to get started with LabMate.</p>
          </div>

          <form onSubmit={handleSubmit} autoComplete="off">
            
            {/* 1. Full Name Input */}
            <div className="input-group">
              <input
                type="text"
                name="username"
                placeholder=" "
                required
                autoComplete="off"
                value={formData.username}
                onChange={handleChange}
              />
              <label>Full Name</label>
            </div>

            {/* 2. Email Input */}
            <div className="input-group">
              <input
                type="email"
                name="email"
                placeholder=" "
                required
                autoComplete="off"
                value={formData.email}
                onChange={handleChange}
              />
              <label>Email Address</label>
            </div>

            {/* 3. Password Input */}
            <div className="input-group">
              <input
                type="password"
                name="password"
                placeholder=" "
                required
                autoComplete="new-password"
                value={formData.password}
                onChange={handleChange}
              />
              <label>Create Password</label>
            </div>

            <button type="submit" className="btn-primary" disabled={isSubmitting}>
              Sign Up
            </button>
          </form>

          {/* Google Signup */}
          <div className="divider">
            <span>OR SIGN UP WITH</span>
          </div>

          <button
            type="button"
            className="btn-google"
            onClick={() => handleGoogleSignup()}
            disabled={isSubmitting}
          >
            <img 
              src="https://www.svgrepo.com/show/475656/google-color.svg" 
              alt="Google" 
              style={{ width: "20px", height: "20px" }} 
            />
            Google
          </button>

          {/* Link to Login */}
          <p className="switch-text">
            Already have an account?
            <button
              type="button"
              className="switch-link"
              onClick={() => navigate("/login")}
            >
              Log in
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

export default Signup;