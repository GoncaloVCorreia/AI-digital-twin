import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PersonaSelector from "../../components/PersonaSelector/PersonaSelector";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import ChatSidebar from "../../components/ChatWindow/ChatSidebar";
import "./ChatView.css";
// import "../../styles.css";
import { fetchConversations, fetchConversationBySessionId, sendMessageToAPI, fetchAllPersonas } from "../../api/chatApi";
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
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [showPersonaPicker, setShowPersonaPicker] = useState(false);
  const [showPersonaCreate, setShowPersonaCreate] = useState(false);
  const [showPersonaCreatedPopup, setShowPersonaCreatedPopup] = useState(false);
  const [isCreatingChat, setIsCreatingChat] = useState(false);
  const [personas, setPersonas] = useState([]);
  const [isLoading, setIsLoading] = useState(true); // Add loading state

  // Fetch personas on mount
  useEffect(() => {
    async function loadPersonas() {
      try {
        const data = await fetchAllPersonas();
        console.log("Fetched personas:", data);
        // Handle different response structures - API returns {items: [], total: ...}
        const personasArray = data?.items || [];
        console.log("Personas array:", personasArray);
        setPersonas(personasArray);
      } catch (err) {
        console.error("Erro ao buscar personas:", err);
        setPersonas([]);
      }
    }
    loadPersonas();
  }, []);

  // Fetch de todas as conversas reais do utilizador
  useEffect(() => {
    const interviewerId = localStorage.getItem("id");
    let mounted = true;

    async function loadConversations() {
      setIsLoading(true); // Start loading
      try {
        const data = await fetchConversations(interviewerId);
        if (mounted) {
          // Handle case where API returns null, undefined, or empty array
          const convList = data || [];
          setConversations(convList);
          
          if (convList.length > 0) {
            // Ordena por data (descendente)
            const sorted = [...convList].sort((a, b) => {
              const ta = new Date(a.created_at || a.updated_at || 0).getTime();
              const tb = new Date(b.created_at || b.updated_at || 0).getTime();
              return tb - ta;
            });
            setCurrentSessionId(sorted[0].session_id);
            setShowPersonaPicker(false);
          } else {
            // No conversations, show persona picker
            setShowPersonaPicker(true);
            setCurrentSessionId(null);
            setCurrentConversation(null);
            setSelectedPersona(null);
          }
        }
      } catch (err) {
        console.error("Erro ao buscar conversas:", err);
        // On error, also show persona picker
        if (mounted) {
          setConversations([]);
          setShowPersonaPicker(true);
          setCurrentSessionId(null);
          setCurrentConversation(null);
          setSelectedPersona(null);
        }
      } finally {
        if (mounted) {
          setIsLoading(false); // End loading
        }
      }
    }

    loadConversations();
    return () => (mounted = false);
  }, []);

  // ✅ Fetch da conversa atual quando o utilizador clica numa
  useEffect(() => {
    if (!conversations || conversations.length === 0 || !currentSessionId) return;
    const conv = conversations.find((c) => c.session_id === currentSessionId);
    if (!conv) return;

    let mounted = true;
    async function loadConversation() {
      try {
        const conv = await fetchConversationBySessionId(currentSessionId);
        if (mounted) setCurrentConversation(conv);
        console.log("Current conversation loaded:", conv);
      } catch (err) {
        console.error("Erro ao buscar conversa:", err);
      }
    }

    loadConversation();
    return () => (mounted = false);
  }, [currentSessionId, conversations]);

  // Sync persona with selected chat
  useEffect(() => {
    if (!conversations || conversations.length === 0 || !currentSessionId) return;
    const conv = conversations.find((c) => c.session_id === currentSessionId);
    if (conv && conv.persona) {
      setSelectedPersona(conv.persona);
    }
  }, [currentSessionId, conversations]);

  function onSelectConversation(sessionId) {
    setCurrentSessionId(sessionId);
    setShowPersonaPicker(false);
    setShowPersonaCreate(false);
    const conv = conversations.find((c) => c.session_id === sessionId);
    if (conv && conv.persona) {
      setSelectedPersona(conv.persona);
    } else if (!sessionId) {
      setSelectedPersona(null);
      setCurrentConversation(null);
    }
  }

  // Add handler to refresh conversations after sending a message
  async function handleSendMessage(chatId, msg) {
    // reload current conversation
    if (currentSessionId && currentConversation) {
      try {
        const updatedConv = await fetchConversationBySessionId(currentSessionId);
        setCurrentConversation(updatedConv);
      } catch (err) {
        console.error("Error reloading conversation:", err);
      }
    }
    
    // reload conversations list to update sidebar last message
    try {
      const interviewerId = localStorage.getItem("id");
      const updatedList = await fetchConversations(interviewerId);
      setConversations(updatedList);
    } catch (err) {
      console.error("Error fetching conversations:", err);
    }
  }

  // Corrigir lógica para garantir que seleciona a conversa nova correta
  async function handleNewChat(persona) {
    setCurrentConversation(null);
    try {
      const interviewerId = localStorage.getItem("id");
      await sendMessageToAPI(null, persona, "Olá!");
      const updatedList = await fetchConversations(interviewerId);
      setConversations(updatedList);

      let newConv = null;
      if (updatedList.length > conversations.length) {
        const oldSessionIds = new Set(conversations.map(c => c.session_id));
        newConv = updatedList.find(c => !oldSessionIds.has(c.session_id) && c.persona === persona);
      }
      if (!newConv) {
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
        setCurrentSessionId(newConv.session_id);
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
    setIsCreatingChat(true); // Show loading immediately
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
    // Reload personas after creating a new one
    fetchAllPersonas()
      .then(data => {
        const personasArray = data?.items || [];
        setPersonas(personasArray);
      })
      .catch(err => console.error("Erro ao recarregar personas:", err));
  }

  function handleCancelPersonaCreate() {
    setShowPersonaCreate(false);
    setShowPersonaPicker(true);
  }

  function handleConversationsUpdate(updatedList) {
    console.log("=== handleConversationsUpdate called ===");
    setConversations(updatedList);
    
    if (updatedList.length === 0) {
      console.log("No conversations left, showing persona picker");
      setShowPersonaPicker(true);
      setCurrentSessionId(null);
      setCurrentConversation(null);
      setSelectedPersona(null);
    }
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
            {isLoading ? (
              <div className="right-panel" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ textAlign: 'center', color: '#3a8bfd', fontSize: '1.2rem', fontWeight: 600 }}>
                  A carregar...
                </div>
              </div>
            ) : showPersonaCreate ? (
              <div className="right-panel persona-create-panel">
                <PersonaCreateForm
                  onCreated={handlePersonaCreated}
                  onCancel={handleCancelPersonaCreate}
                />
              </div>
            ) : showPersonaPicker || conversations.length === 0 ? (
              <div className="right-panel persona-picker-panel">
                <div className="persona-picker-row" style={{ flexDirection: "column", gap: "0" }}>
                  <PersonaSelector
                    horizontal
                    selected={null}
                    setSelected={handlePersonaPick}
                    showAddButton={true}
                    onAddClick={handleShowPersonaCreate}
                    personas={personas}
                    disabled={isCreatingChat}
                  />
                  {conversations.length > 0 && (
                    <button
                      className="new-chat-btn persona-cancel-btn"
                      style={{ marginTop: "32px" }}
                      onClick={() => setShowPersonaPicker(false)}
                      disabled={isCreatingChat}
                    >
                      Cancelar
                    </button>
                  )}
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
                    personas={personas}
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
          currentSessionId={currentSessionId}
          onSelectConversation={onSelectConversation}
          onNewChat={handleNewChatButton}
          onConversationsUpdate={handleConversationsUpdate}
        />
      </div>
    </div>
  );
}
