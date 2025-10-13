import { useState } from "react";
import PersonaSelector from "../../components/PersonaSelector/PersonaSelector";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import { useNavigate } from "react-router-dom";

import "./ChatView.css";
import "../../styles.css";

export default function ChatView() {
  const navigate = useNavigate();
  const username = localStorage.getItem("username");

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    navigate("/login");
  }
  const [selectedPersona, setSelectedPersona] = useState("Rafael");

  return (
    <div className="chat-view">
      {" "}
      <header className="chat-header">
        <div className="user-info">
          <span className="username">👤 {username}</span>
        </div>
        <div className="header-buttons">
          <button className="home-btn" onClick={() => navigate("/")}>
            Home
          </button>
          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </header>
      <h1 className="chat-title">Digital Twin Chatbot 🤖</h1>
      {/* container absoluto abaixo do título */}
      <div className="persona-target" />
      <div>
        <PersonaSelector
          selected={selectedPersona}
          setSelected={setSelectedPersona}
        />
        <div
          style={{ marginTop: "-200px" }} // move o chat para cima
        >
          <ChatWindow persona={selectedPersona} />
        </div>
      </div>
    </div>
  );
}
