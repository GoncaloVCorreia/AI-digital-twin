// src/components/MessageBubble/MessageBubble.jsx
import React from "react";
import "./MessageBubble.css";

export default function MessageBubble({ role, content, text }) {
  // usamos content se existir, caso contrário text
  const messageText = content || text;

  // Classes para alinhar à esquerda/direita
  let bubbleClass = "message-bubble";
  if (role === "user") bubbleClass += " user";
  else bubbleClass += " assistant"; // system e assistant à esquerda

  return <div className={bubbleClass}>{messageText}</div>;
}
