// src/components/ChatWindow/ChatSidebar.jsx
import React from "react";
import "./ChatSidebar.css";
import { deleteConversationBySessionId, fetchConversations } from "../../api/chatApi";

export default function ChatSidebar({
  conversations,
  currentChatId,
  onSelectConversation,
  onNewChat,
}) {
  // Adiciona função para apagar conversa e atualizar lista
  async function handleDeleteConversation(conv) {
    if (!window.confirm("Apagar esta conversa?")) return;
    try {
      await deleteConversationBySessionId(conv.session_id);
      // Atualiza conversas após apagar
      const interviewerId = localStorage.getItem("id");
      const updatedList = await fetchConversations(interviewerId);
      // Se a conversa apagada era a selecionada, limpa seleção
      if (conv.id === currentChatId && updatedList.length > 0) {
        onSelectConversation(updatedList[0].id);
      }
      // Se não houver conversas, limpa seleção
      if (updatedList.length === 0) {
        onSelectConversation(null);
      }
    } catch (err) {
      alert("Erro ao apagar conversa.");
    }
  }

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
              const isSelected = String(conv.id) === String(currentChatId);
              return (
                <li
                  key={conv.id}
                  className={`chat-item${
                    isSelected ? " selected" : ""
                  }`}
                  onClick={() => onSelectConversation(conv.id)}
                  style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}
                >
                  <span style={{ flex: 1, cursor: "pointer" }}>
                    {lastMsg}
                  </span>
                  <button
                    className="delete-chat-btn"
                    title="Apagar conversa"
                    onClick={e => {
                      e.stopPropagation();
                      handleDeleteConversation(conv);
                    }}
                    style={{
                      background: "none",
                      border: "none",
                      cursor: "pointer",
                      padding: "0 6px",
                      marginLeft: "8px",
                      display: "flex",
                      alignItems: "center"
                    }}
                  >
                    {/* Trash SVG icon */}
                    <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
                      <path d="M7 9v5m3-5v5m-7 2a2 2 0 002 2h8a2 2 0 002-2V7H3v9zm5-16a2 2 0 012 2v1H7V3a2 2 0 012-2zm7 4H4" stroke="#000000ff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </button>
                </li>
              );
            })}
        </ul>
      </div>
    </aside>
  );
}
