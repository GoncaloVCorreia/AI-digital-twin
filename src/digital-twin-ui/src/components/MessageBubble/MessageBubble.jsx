// src/components/MessageBubble/MessageBubble.jsx
import React from "react";
import "./MessageBubble.css";

// role: "user" or "assistant", content: string
export default function MessageBubble({ role, content }) {
  return (
    <div className={`message-bubble ${role}`}>
      {content}
    </div>
  );
}
