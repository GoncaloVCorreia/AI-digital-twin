import React, { useState, useEffect, useRef } from "react";
import MessageBubble from "../MessageBubble/MessageBubble.jsx";
import { sendMessageToAPI } from "../../api/chatApi";
import "./ChatWindow.css";

export default function ChatWindow({ persona, conversation, onSendMessage }) {
  const [chat, setChat] = useState([]);
  const [message, setMessage] = useState("");
  const messagesRef = useRef(null);
  const lastSessionIdRef = useRef(null);

  // Only reset chat when switching to a different session
  useEffect(() => {
    if (
      conversation &&
      conversation.session_id &&
      conversation.session_id !== lastSessionIdRef.current
    ) {
      lastSessionIdRef.current = conversation.session_id;
      setChat(conversation.messages ? conversation.messages.slice() : []);
      setTimeout(() => {
        const el = messagesRef.current;
        if (el) el.scrollTop = el.scrollHeight;
      }, 10);
    }
    // If conversation is null, clear chat
    if (!conversation) {
      lastSessionIdRef.current = null;
      setChat([]);
    }
  }, [conversation]);

  // Scroll automático sempre que chat muda (envio ou receção)
  useEffect(() => {
    const el = messagesRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [chat]);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMsg = { role: "user", text: message };
    setChat((prev) => [...prev, userMsg]);
    setMessage("");

    if (conversation && onSendMessage) {
      onSendMessage(conversation.id, userMsg);
    }

    // Use real API to send message and get assistant reply
    if (conversation && conversation.session_id) {
      try {
        const res = await sendMessageToAPI(
          conversation.session_id,
          persona,
          message
        );
        // Show the last assistant message from API response
        let assistantText = "";
        if (res && res.messages && Array.isArray(res.messages)) {
          // Find the last assistant message
          const assistantMsgs = res.messages.filter((m) => m.role === "assistant");
          if (assistantMsgs.length > 0) {
            assistantText = assistantMsgs[assistantMsgs.length - 1].content;
          }
        } else if (res.reply) {
          assistantText = res.reply;
        } else if (res.message) {
          assistantText = res.message;
        }
        const aiMsg = {
          role: "assistant",
          text: assistantText,
        };
        setChat((prev) => [...prev, aiMsg]);
        if (conversation && onSendMessage) {
          onSendMessage(conversation.id, aiMsg);
        }
      } catch (err) {
        const aiMsg = {
          role: "assistant",
          text: "Erro ao obter resposta do assistente.",
        };
        setChat((prev) => [...prev, aiMsg]);
      }
    }

    // scroll down after reply
    setTimeout(() => {
      const el = messagesRef.current;
      if (el) el.scrollTop = el.scrollHeight;
    }, 50);
  };

  // Obter nome da persona para título
  const personaName = persona ? persona.charAt(0).toUpperCase() + persona.slice(1) : "";

  return (
    <div className="chat-window">
      {/* Título da persona no topo da janela */}
      <div className="chat-persona-title">
        {personaName && (
          <span>
            {personaName}
          </span>
        )}
      </div>
      <div className="messages" ref={messagesRef}>
        {chat
          .filter((m) => m.role === "user" || m.role === "assistant")
          .map((m, i) => (
            <MessageBubble
              key={i}
              role={m.role}
              content={m.content || m.text}
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
