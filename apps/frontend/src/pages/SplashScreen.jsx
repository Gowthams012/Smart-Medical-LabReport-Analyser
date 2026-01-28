import React, { useState, useEffect } from "react";
import "./styles/SplashScreen.css";

const SplashScreen = ({ onComplete }) => {
  const [isFading, setIsFading] = useState(false);

  useEffect(() => {
    // 1. Wait for the loading bar animation (2.8s) + a tiny buffer
    const timer = setTimeout(() => {
      setIsFading(true); // Trigger fade out class
    }, 3000);

    // 2. Actually unmount the component after fade transition (0.8s)
    const cleanup = setTimeout(() => {
      if (onComplete) onComplete();
    }, 3800);

    return () => {
      clearTimeout(timer);
      clearTimeout(cleanup);
    };
  }, [onComplete]);

  return (
    <div className={`splash-container ${isFading ? "hidden" : ""}`}>
      {/* 3D Holographic Gyroscope */}
      <div className="scene">
        <div className="gyroscope">
          <div className="ring"></div>
          <div className="ring"></div>
          <div className="ring"></div>
          <div className="core"></div>
        </div>
      </div>

      {/* Modern Branding */}
      <h1 className="brand-name">labmate.ai</h1>
      <div className="tagline">Smart Lab Analyser</div>

      {/* Progress Bar */}
      <div className="loading-bar-container">
        <div className="loading-bar"></div>
      </div>
    </div>
  );
};

export default SplashScreen;
