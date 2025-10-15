// src/components/ChatWindow/ChatSidebar.jsx
import React from "react";
import "./ChatSidebar.css";

export default function ChatSidebar({
  conversations,
  currentChatId,
  onSelectConversation,
  onNewChat,
}) {
  return (
    <aside className="chat-sidebar">
      <div className="sidebar-header sidebar-header--sticky">
        <h3 className="sidebar-title">Chats</h3>
        <button className="new-chat-btn" onClick={onNewChat}>
          Novo Chat
        </button>
      </div>
      <div className="sidebar-scrollable">
        <ul>
          {[...conversations]
            .sort((a, b) => {
              // Extrai até aos segundos (YYYY-MM-DDTHH:MM:SS)
              function extractDate(str) {
                if (!str) return null;
                const match = str.match(/^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})/);
                return match ? match[1] : null;
              }
              const aDateStr = extractDate(a.created_at);
              const bDateStr = extractDate(b.created_at);
              if (!aDateStr && !bDateStr) return 0;
              if (!aDateStr) return 1;
              if (!bDateStr) return -1;
              // Compare como Date
              return new Date(bDateStr) - new Date(aDateStr);
            })
            .map((conv) => {
              // encontra a última mensagem válida (user ou assistant)
              const lastMsgObj = conv.messages
                ? [...conv.messages]
                    .reverse()
                    .find((m) => m.role === "user" || m.role === "assistant")
                : null;
              let lastMsg = lastMsgObj
                ? lastMsgObj.content || lastMsgObj.text
                : "Sem mensagens";
              // Garante que lastMsg é string antes de split
              if (typeof lastMsg !== "string" || !lastMsg) {
                lastMsg = "Sem mensagens";
              }
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
      </div>
    </aside>
  );
}
