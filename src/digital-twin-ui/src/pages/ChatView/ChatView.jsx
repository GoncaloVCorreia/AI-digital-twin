import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PersonaSelector from "../../components/PersonaSelector/PersonaSelector";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import ChatSidebar from "../../components/ChatWindow/ChatSidebar";
import "./ChatView.css";
import "../../styles.css";
import { fetchConversations, fetchConversationBySessionId, sendMessageToAPI } from "../../api/chatApi";

export default function ChatView() {
  const navigate = useNavigate();
  const username = localStorage.getItem("username");

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    localStorage.removeItem("id");
    navigate("/login");
  }

  // Remover hardcoded persona inicial
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [showPersonaPicker, setShowPersonaPicker] = useState(false);

  // Fetch de todas as conversas reais do utilizador
  useEffect(() => {
    const interviewerId = localStorage.getItem("id");
    let mounted = true;

    async function loadConversations() {
      try {
        const data = await fetchConversations(interviewerId);
        if (mounted) {
          setConversations(data);
          // Seleciona automaticamente a conversa mais recente
          if (data.length > 0) {
            // Ordena por data (descendente)
            const sorted = [...data].sort((a, b) => {
              const ta = new Date(a.created_at || a.updated_at || 0).getTime();
              const tb = new Date(b.created_at || b.updated_at || 0).getTime();
              return tb - ta;
            });
            setCurrentChatId(sorted[0].id);
          }
        }
      } catch (err) {
        console.error("Erro ao buscar conversas:", err);
      }
    }

    loadConversations();
    return () => (mounted = false);
  }, []);

  // ✅ Fetch da conversa atual quando o utilizador clica numa
  useEffect(() => {
    if (!conversations || conversations.length === 0 || !currentChatId) return;
    const conv = conversations.find((c) => c.id === currentChatId);
    if (!conv) return;
    const { session_id } = conv;

    let mounted = true;
    async function loadConversation() {
      try {
        const conv = await fetchConversationBySessionId(session_id);
        if (mounted) setCurrentConversation(conv);
        console.log("Current conversation loaded:", conv);
      } catch (err) {
        console.error("Erro ao buscar conversa:", err);
      }
    }

    loadConversation();
    return () => (mounted = false);
  }, [currentChatId, conversations]);

  // Sync persona with selected chat whenever currentChatId or conversations change
  useEffect(() => {
    if (!conversations || conversations.length === 0 || !currentChatId) return;
    const conv = conversations.find((c) => c.id === currentChatId);
    if (conv && conv.persona) {
      setSelectedPersona(conv.persona);
    }
    // Remover else que coloca null
  }, [currentChatId, conversations]);

  function onSelectConversation(id) {
    setCurrentChatId(id);
    const conv = conversations.find((c) => c.id === id);
    if (conv && conv.persona) {
      setSelectedPersona(conv.persona);
    }
    // Remover else que coloca null
  }

  // Add handler to refresh conversations after sending a message
  async function handleSendMessage(chatId, msg) {
    // reload current conversation
    if (currentChatId && currentConversation) {
      const conv = conversations.find((c) => c.id === currentChatId);
      if (conv && conv.session_id) {
        try {
          const updatedConv = await fetchConversationBySessionId(conv.session_id);
          setCurrentConversation(updatedConv);
        } catch (err) {
          // ignore error
        }
      }
    }
    // reload conversations list to update sidebar last message
    try {
      const interviewerId = localStorage.getItem("id");
      const updatedList = await fetchConversations(interviewerId);
      setConversations(updatedList);
    } catch (err) {
      // ignore error
    }
  }

  // Corrigir lógica para garantir que seleciona a conversa nova correta
  async function handleNewChat(persona) {
    try {
      const interviewerId = localStorage.getItem("id");
      await sendMessageToAPI(null, persona, "Olá!");
      const updatedList = await fetchConversations(interviewerId);
      setConversations(updatedList);

      // Encontrar a conversa mais recente que ainda não estava na lista anterior
      let newConv = null;
      if (updatedList.length > conversations.length) {
        // Nova conversa é aquela que não estava antes
        const oldIds = new Set(conversations.map(c => c.id));
        newConv = updatedList.find(c => !oldIds.has(c.id) && c.persona === persona);
      }
      if (!newConv) {
        // fallback: encontrar a mais recente para a persona
        const personaConvs = updatedList.filter(c => c.persona === persona);
        if (personaConvs.length > 0) {
          personaConvs.sort((a, b) => {
            const ta = new Date(a.created_at || a.updated_at || 0).getTime();
            const tb = new Date(b.created_at || b.updated_at || 0).getTime();
            return tb - ta;
          });
          newConv = personaConvs[0];
        }
      }
      if (newConv) {
        setCurrentChatId(newConv.id);
        setSelectedPersona(newConv.persona);
        if (newConv.session_id) {
          const conv = await fetchConversationBySessionId(newConv.session_id);
          setCurrentConversation(conv);
        }
      }
    } catch (err) {
      alert("Erro ao criar novo chat.");
    }
  }

  async function handleNewChatButton() {
    setShowPersonaPicker(true);
  }

  async function handlePersonaPick(persona) {
    setShowPersonaPicker(false);
    await handleNewChat(persona);
  }

  return (
    <div className="chat-view">
      <header className="chat-header">
        <div className="user-info">
          <span className="username">👤 {username}</span>
        </div>
        <div className="header-buttons">
          <button className="home-btn" onClick={() => navigate("/")}>
            Home
          </button>
          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      <div className="chat-main-grid">
        <div className="chat-main-content">
          <h1 className="chat-title">Digital Twin Chatbot 🤖</h1>

          <div className="chat-container">
            {showPersonaPicker ? (
              <div
                className="right-panel persona-picker-panel"
                style={{
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  alignItems: "center",
                  height: "100%",
                  minHeight: "350px"
                }}
              >
                <div
                  style={{
                    display: "flex",
                    flexDirection: "row",
                    justifyContent: "center",
                    alignItems: "center",
                    gap: "30px",
                    marginTop: "10px",
                    marginBottom: "30px"
                  }}
                >
                  {["rafael", "garcia", "correia", "francisco"].map((p) => (
                    <div
                      key={p}
                      className="persona-circle"
                      style={{
                        width: "80px",
                        height: "80px",
                        fontSize: "1.2rem",
                        background: "#f1f1f1",
                        border: "2px solid #ccc",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontWeight: "bold",
                        transition: "all 0.3s"
                      }}
                      onClick={() => handlePersonaPick(p)}
                    >
                      <span className="persona-name">{p}</span>
                    </div>
                  ))}
                </div>
                <button
                  className="new-chat-btn"
                  style={{
                    width: "auto",
                    padding: "8px 24px",
                    display: "block",
                    marginLeft: "auto",
                    marginRight: "auto"
                  }}
                  onClick={() => setShowPersonaPicker(false)}
                >
                  Cancelar
                </button>
              </div>
            ) : (
              <div className="right-panel">
                <aside className="persona-panel">
                  <PersonaSelector
                    selected={selectedPersona}
                    setSelected={setSelectedPersona}
                    persona={selectedPersona} // <-- Adiciona esta prop
                  />
                </aside>

                <div className="chat-area">
                  <ChatWindow
                    persona={selectedPersona}
                    conversation={currentConversation}
                    onSendMessage={handleSendMessage}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Mantém sidebar à direita */}
        <ChatSidebar
          conversations={conversations}
          currentChatId={currentChatId}
          onSelectConversation={onSelectConversation}
          onNewChat={handleNewChatButton}
        />
      </div>
    </div>
  );
}
