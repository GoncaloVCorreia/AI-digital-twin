// src/components/ChatWindow/ChatSidebar.jsx
import React from "react";
import "./ChatSidebar.css";

export default function ChatSidebar({
  conversations,
  currentChatId,
  onSelectConversation,
}) {
  return (
    <aside className="chat-sidebar">
      <div>
        {/* Put the title "Conversas" in the middle of the sidebar */}
        <h3 className="sidebar-title">Conversas</h3>
        <button className="new-chat-btn" onClick={() => onSelectConversation(null)}>
          Novo Chat
        </button>
      </div>

      <ul>
        {conversations.map((conv) => {
          // encontra a última mensagem válida (user ou assistant)
          const lastMsgObj = conv.messages
            ? [...conv.messages]
                .reverse()
                .find((m) => m.role === "user" || m.role === "assistant")
            : null;
          let lastMsg = lastMsgObj
            ? lastMsgObj.content || lastMsgObj.text
            : "Sem mensagens";
          if (lastMsg !== "Sem mensagens") {
            const words = lastMsg.split(/\s+/);
            lastMsg = words.slice(0, 5).join(" ");
            if (words.length > 5) lastMsg += " ...";
          }
          return (
            <li
              key={conv.id}
              className={conv.id === currentChatId ? "selected" : ""}
              onClick={() => onSelectConversation(conv.id)}
            >
              {lastMsg}
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
