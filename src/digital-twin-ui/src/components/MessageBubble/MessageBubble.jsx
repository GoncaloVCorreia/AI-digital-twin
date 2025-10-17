// src/components/MessageBubble/MessageBubble.jsx
import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./MessageBubble.css";

// role: "user" or "assistant", content: string
export default function MessageBubble({ role, content }) {
  // Simple check for markdown patterns (tables, links, headers, etc.)
  const hasMarkdown = /[|#*_`[\]]/.test(content);

  return (
    <div className={`message-bubble ${role}`}>
      {hasMarkdown ? (
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      ) : (
        content
      )}
    </div>
  );
}
