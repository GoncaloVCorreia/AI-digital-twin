import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./HomePage.css";

export default function HomePage() {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const username = localStorage.getItem("username");

  // Check authentication status on mount
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    setIsLoggedIn(!!token);
  }, []);

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    localStorage.removeItem("id");
    setIsLoggedIn(false);
  }

  return (
    <div className="home-container">
      <div className="home-content-box">
        <h1>🤖 Digital Twin Chatbot</h1>
        <p className="subtitle">Making interviews easier and more autonomous</p>

        {isLoggedIn && username && (
          <h2 className="welcome">Bem-vindo, {username} 👋</h2>
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
