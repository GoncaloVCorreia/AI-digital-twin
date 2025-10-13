import React from "react";
import { useNavigate } from "react-router-dom";
import "./HomePage.css";

export default function HomePage() {
  const navigate = useNavigate();
  const username = localStorage.getItem("username");
  const token = localStorage.getItem("access_token");

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    navigate("/login");
  }

  return (
    <div className="home-container">
      <h1>🤖 Digital Twin Chatbot</h1>
      <p className="subtitle">Making interviews easier and more autonomous</p>

      {username && <h2 className="welcome">Bem-vindo, {username} 👋</h2>}

      <div className="home-buttons">
        {/* Só mostra login e register se não estiver autenticado */}
        {!token && (
          <>
            <button onClick={() => navigate("/login")}>Login</button>
            <button onClick={() => navigate("/register")}>Register</button>
          </>
        )}

        {/* Mostra logout apenas se estiver autenticado */}
        {token && <button onClick={logout}>Logout</button>}
        {token && <button onClick={() => navigate("/chat")}>Go to Chat</button>}
      </div>
    </div>
  );
}
