import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./HomePage.css";
import { useTheme } from "../../contexts/ThemeContext";

export default function HomePage() {
  const { darkMode, toggleDarkMode } = useTheme();
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");

  // Check authentication status on mount and when storage changes
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem("access_token");
      const storedUsername = localStorage.getItem("username");
      setIsLoggedIn(!!token);
      setUsername(storedUsername || "");
    };

    checkAuth();

    // Listen for storage changes (e.g., logout in another tab)
    window.addEventListener("storage", checkAuth);
    return () => window.removeEventListener("storage", checkAuth);
  }, []);

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    localStorage.removeItem("id");
    setIsLoggedIn(false);
    setUsername("");
  }

  return (
    <div className="home-container">
      <button 
        className="theme-toggle-btn" 
        onClick={toggleDarkMode}
        title={darkMode ? "Light Mode" : "Dark Mode"}
      >
        {darkMode ? "☀️" : "🌙"}
      </button>
      <div className="home-content-box">
        <h1>🤖 Digital Twin Chatbot</h1>
        <p className="subtitle">Making interviews easier and more autonomous</p>

        {isLoggedIn && username && (
          <h2 className="welcome">Welcome, {username} 👋</h2>
        )}

        <div className="home-buttons">
          {isLoggedIn ? (
            <>
              <button onClick={() => navigate("/chat")}>Go to Chat</button>
              <button onClick={logout}>Logout</button>
            </>
          ) : (
            <>
              <button onClick={() => navigate("/login")}>Login</button>
              <button onClick={() => navigate("/register")}>Register</button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
