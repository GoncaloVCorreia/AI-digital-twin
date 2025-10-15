import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PersonaSelector from "../../components/PersonaSelector/PersonaSelector";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import ChatSidebar from "../../components/ChatWindow/ChatSidebar";
import "./ChatView.css";
// import "../../styles.css";
import { fetchConversations, fetchConversationBySessionId, sendMessageToAPI } from "../../api/chatApi";
import PersonaCreateForm from "../../components/PersonaSelector/PersonaCreateForm";

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
  const [showPersonaCreate, setShowPersonaCreate] = useState(false);
  const [showPersonaCreatedPopup, setShowPersonaCreatedPopup] = useState(false);
  const [isCreatingChat, setIsCreatingChat] = useState(false);
  

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
    setShowPersonaPicker(false);
    setShowPersonaCreate(false); // fecha o form de criação se estiver aberto
    const conv = conversations.find((c) => c.id === id);
    if (conv && conv.persona) {
      setSelectedPersona(conv.persona);
    }
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
    setIsCreatingChat(true);
    setCurrentConversation(null); // Clear current conversation immediately
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
    } finally {
      setIsCreatingChat(false);
    }
  }

  async function handleNewChatButton() {
    setShowPersonaPicker(true);
    setShowPersonaCreate(false); // fecha o form de criação se estiver aberto
  }

  async function handlePersonaPick(persona) {
    setShowPersonaPicker(false);
    await handleNewChat(persona);
  }

  function handleShowPersonaCreate() {
    setShowPersonaPicker(false);
    setShowPersonaCreate(true);
  }

  function handlePersonaCreated() {
    setShowPersonaCreate(false);
    setShowPersonaPicker(true);
    setShowPersonaCreatedPopup(true);
    setTimeout(() => setShowPersonaCreatedPopup(false), 2000);
  }

  function handleCancelPersonaCreate() {
    setShowPersonaCreate(false);
    setShowPersonaPicker(true);
  }

  return (
    <div className="chat-view">
      <header className="chat-header">
        <div className="user-info">
          <span className="username">👤 {username}</span>
        </div>
        {/* Usa classe para o texto centralizado */}
        <div className="chat-header-title">
          Digital Twin Chatbot 🤖
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
      {showPersonaCreatedPopup && (
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
          Persona criada com sucesso!
        </div>
      )}
      <div className="chat-main-grid">
        <div className="chat-main-content">
          <div className="chat-container">
            {showPersonaCreate ? (
              <div className="right-panel persona-create-panel">
                <PersonaCreateForm
                  onCreated={handlePersonaCreated}
                  onCancel={handleCancelPersonaCreate}
                />
              </div>
            ) : showPersonaPicker ? (
              <div className="right-panel persona-picker-panel">
                <div className="persona-picker-row" style={{ flexDirection: "column", gap: "0" }}>
                  <PersonaSelector
                    horizontal
                    selected={null}
                    setSelected={handlePersonaPick}
                    showAddButton={true}
                    onAddClick={handleShowPersonaCreate}
                  />
                  <button
                    className="new-chat-btn persona-cancel-btn"
                    style={{ marginTop: "32px" }}
                    onClick={() => setShowPersonaPicker(false)}
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            ) : isCreatingChat ? (
              <div className="right-panel" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ textAlign: 'center', color: '#3a8bfd', fontSize: '1.2rem', fontWeight: 600 }}>
                  A criar novo chat...
                </div>
              </div>
            ) : (
              <div className="right-panel">
                <aside className="persona-panel">
                  <PersonaSelector
                    selected={selectedPersona}
                    setSelected={setSelectedPersona}
                    persona={selectedPersona}
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
