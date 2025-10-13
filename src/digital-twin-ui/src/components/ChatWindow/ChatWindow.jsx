import React, { useState } from "react";
import MessageBubble from "../MessageBubble/MessageBubble.jsx";
import { sendMessageToMockAPI } from "../../api/mockApi";
import "./ChatWindow.css";

export default function ChatWindow({ persona }) {
  const [chat, setChat] = useState([]);
  const [message, setMessage] = useState("");

  const sendMessage = async () => {
    if (!message.trim()) return;
    const userMsg = { role: "user", text: message };
    setChat((prev) => [...prev, userMsg]);
    setMessage("");

    const res = await sendMessageToMockAPI(message, persona);
    const aiMsg = { role: "ai", text: res.reply };
    setChat((prev) => [...prev, aiMsg]);
  };

  return (
    <div className="chat-window">
      <div className="messages">
        {chat.map((m, i) => (
          <MessageBubble key={i} {...m} />
        ))}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={message}
          placeholder="Escreve uma mensagem..."
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage}>Enviar</button>
      </div>
    </div>
  );
}
