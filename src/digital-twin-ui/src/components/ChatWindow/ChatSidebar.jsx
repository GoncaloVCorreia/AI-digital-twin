// src/components/ChatWindow/ChatSidebar.jsx
import React, { useState } from "react";
import "./ChatSidebar.css";
import { deleteConversationBySessionId, fetchConversations } from "../../api/chatApi";

export default function ChatSidebar({
  conversations,
  currentSessionId,
  onSelectConversation,
  onNewChat,
  onConversationsUpdate,
}) {
  const [showDeletePopup, setShowDeletePopup] = useState(false);
  const [showConfirmPopup, setShowConfirmPopup] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState(null);

  // Adiciona função para apagar conversa e atualizar lista
  async function handleDeleteConversation(conv) {
    const interviewerId = localStorage.getItem("id");
    
    try {
      await deleteConversationBySessionId(conv.session_id);
      console.log("Conversation deleted successfully");
      
      // Show success popup immediately
      setShowDeletePopup(true);
      setTimeout(() => setShowDeletePopup(false), 2000);
      
    } catch (err) {
      console.error("Erro ao apagar conversa:", err);
    }
    
    // Always try to refresh, even if deletion had an error
    try {
      const updatedList = await fetchConversations(interviewerId);
      console.log("Fetched updated list after deletion:", updatedList);
      
      // Notify parent to update conversations
      if (onConversationsUpdate) {
        console.log("Calling onConversationsUpdate with:", updatedList);
        onConversationsUpdate(updatedList);
      }
      
      // Handle selection after update
      if (conv.session_id === currentSessionId) {
        if (updatedList.length > 0) {
          console.log("Selecting first conversation:", updatedList[0].session_id);
          onSelectConversation(updatedList[0].session_id);
        } else {
          console.log("No conversations left, clearing selection");
          onSelectConversation(null);
        }
      }
    } catch (refreshErr) {
      console.error("Erro ao atualizar lista:", refreshErr);
      console.log("Error fetching conversations (likely 404), treating as empty list");
      
      if (onConversationsUpdate) {
        onConversationsUpdate([]);
      }
      
      onSelectConversation(null);
    }
  }

  function confirmDelete(conv) {
    setConversationToDelete(conv);
    setShowConfirmPopup(true);
  }

  function handleConfirmDelete() {
    if (conversationToDelete) {
      handleDeleteConversation(conversationToDelete);
    }
    setShowConfirmPopup(false);
    setConversationToDelete(null);
  }

  function handleCancelDelete() {
    setShowConfirmPopup(false);
    setConversationToDelete(null);
  }

  return (
    <aside className="chat-sidebar">
      {showDeletePopup && (
        <div
          style={{
            position: "fixed",
            top: "80px",
            left: "50%",
            transform: "translateX(-50%)",
            background: "#3a8bfd",
            color: "#fff",
            padding: "16px 32px",
            borderRadius: "12px",
            fontWeight: 600,
            fontSize: "1.15rem",
            zIndex: 9999,
            boxShadow: "0 2px 12px rgba(58,139,253,0.18)",
            transition: "opacity 0.3s"
          }}
        >
          Conversation deleted successfully!
        </div>
      )}
      {showConfirmPopup && (
        <>
          <div
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "rgba(0,0,0,0.5)",
              zIndex: 9998,
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}
            onClick={handleCancelDelete}
          >
            <div
              style={{
                background: "#fff",
                padding: "32px",
                borderRadius: "16px",
                maxWidth: "400px",
                width: "90%",
                boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
                textAlign: "center"
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 style={{ margin: "0 0 16px 0", fontSize: "1.3rem", color: "#222" }}>
                Delete conversation?
              </h3>
              <p style={{ margin: "0 0 24px 0", color: "#666", fontSize: "1rem" }}>
                This action cannot be undone.
              </p>
              <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
                <button
                  onClick={handleCancelDelete}
                  style={{
                    padding: "10px 24px",
                    borderRadius: "8px",
                    border: "none",
                    background: "#ddd",
                    color: "#222",
                    fontWeight: 600,
                    cursor: "pointer",
                    fontSize: "1rem",
                    transition: "background 0.2s"
                  }}
                  onMouseEnter={(e) => (e.target.style.background = "#bbb")}
                  onMouseLeave={(e) => (e.target.style.background = "#ddd")}
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmDelete}
                  style={{
                    padding: "10px 24px",
                    borderRadius: "8px",
                    border: "none",
                    background: "#e74c3c",
                    color: "#fff",
                    fontWeight: 600,
                    cursor: "pointer",
                    fontSize: "1rem",
                    transition: "background 0.2s"
                  }}
                  onMouseEnter={(e) => (e.target.style.background = "#c0392b")}
                  onMouseLeave={(e) => (e.target.style.background = "#e74c3c")}
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </>
      )}
      <div className="sidebar-header sidebar-header--sticky">
        <h3 className="sidebar-title">Chats</h3>
        <button className="new-chat-btn" onClick={onNewChat}>
          New Chat
        </button>
      </div>
      <div className="sidebar-scrollable">
        {conversations.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '24px 12px',
            color: '#666',
            fontSize: '1rem'
          }}>
            No conversations yet. Click "New Chat" to start one!
          </div>
        ) : (
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
                
                // Direct comparison - no need for local state
                const isSelected = currentSessionId !== null && conv.session_id === currentSessionId;
                
                return (
                  <li
                    key={conv.session_id}
                    className={`chat-item${isSelected ? " selected" : ""}`}
                    onClick={() => onSelectConversation(conv.session_id)}
                    style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}
                  >
                    <span style={{ flex: 1, cursor: "pointer" }}>
                      {lastMsg}
                    </span>
                    <button
                      className="delete-chat-btn"
                      title="Delete conversation"
                      onClick={e => {
                        e.stopPropagation();
                        confirmDelete(conv);
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
        )}
      </div>
    </aside>
  );
}
