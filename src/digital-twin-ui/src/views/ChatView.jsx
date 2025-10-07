import { useState } from "react";
import PersonaSelector from "../components/PersonaSelector/PersonaSelector";
import ChatWindow from "../components/ChatWindow/ChatWindow";
import "../styles.css"; // global styles

export default function ChatView() {
  const [selectedPersona, setSelectedPersona] = useState("Rafael");

  return (
    <div className="app-container">
      <h1>Digital Twin Chatbot 🤖</h1>
      <PersonaSelector selected={selectedPersona} setSelected={setSelectedPersona} />
      <ChatWindow persona={selectedPersona} />
    </div>
  );
}
