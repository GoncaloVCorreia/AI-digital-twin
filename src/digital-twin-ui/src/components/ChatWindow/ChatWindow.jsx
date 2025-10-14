import React, { useState, useEffect, useRef } from "react";
import MessageBubble from "../MessageBubble/MessageBubble.jsx";
import { sendMessageToMockAPI } from "../../api/mockApi";
import "./ChatWindow.css";

export default function ChatWindow({ persona, conversation, onSendMessage }) {
  const [chat, setChat] = useState([]);
  const [message, setMessage] = useState("");
  const messagesRef = useRef(null);

  // Inicializa chat quando conversation muda
  useEffect(() => {
    if (conversation && conversation.messages) {
      setChat(conversation.messages.slice());

      // scroll para baixo após render
      setTimeout(() => {
        const el = messagesRef.current;
        if (el) el.scrollTop = el.scrollHeight;
      }, 10);
    } else {
      setChat([]);
    }
  }, [conversation]);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMsg = { role: "user", text: message };
    setChat((prev) => [...prev, userMsg]);
    setMessage("");

    if (conversation && onSendMessage) {
      onSendMessage(conversation.id, userMsg);
    }

    const res = await sendMessageToMockAPI(message, persona);
    const aiMsg = { role: "assistant", text: res.reply };
    setChat((prev) => [...prev, aiMsg]);
    if (conversation && onSendMessage) {
      onSendMessage(conversation.id, aiMsg);
    }

    // scroll down after reply
    setTimeout(() => {
      const el = messagesRef.current;
      if (el) el.scrollTop = el.scrollHeight;
    }, 50);
  };

  return (
    <div className="chat-window">
      <div className="messages" ref={messagesRef}>
        {/* {chat.map((m, i) => (
          <MessageBubble
            key={i}
            role={m.role}
            content={m.content || m.text} // usa content da API ou text
          />
        ))} */}
        {chat
          .filter((m) => m.role === "user" || m.role === "assistant")
          .map((m, i) => (
            <MessageBubble
              key={i}
              role={m.role}
              content={m.content || m.text} // usa content da API ou text
            />
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
