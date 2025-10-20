import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PersonaSelector from "../../components/PersonaSelector/PersonaSelector";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import ChatSidebar from "../../components/ChatWindow/ChatSidebar";
import "./ChatView.css";
// import "../../styles.css";
import { fetchConversations, fetchConversationBySessionId, sendMessageToAPI, fetchAllPersonas, deletePersonaById, deleteConversationBySessionId } from "../../api/chatApi";
import PersonaCreateForm from "../../components/PersonaSelector/PersonaCreateForm";


export default function ChatView() {
  // Add monitoring for localStorage changes
  useEffect(() => {
    const originalSetItem = localStorage.setItem;
    const originalRemoveItem = localStorage.removeItem;
    const originalClear = localStorage.clear;

    localStorage.setItem = function(key, value) {
      console.log(`📝 localStorage.setItem called:`, key, value);
      console.trace();
      return originalSetItem.apply(this, arguments);
    };

    localStorage.removeItem = function(key) {
      console.log(`🗑️ localStorage.removeItem called:`, key);
      console.trace();
      return originalRemoveItem.apply(this, arguments);
    };

    localStorage.clear = function() {
      console.log(`💥 localStorage.clear called!`);
      console.trace();
      return originalClear.apply(this, arguments);
    };

    return () => {
      localStorage.setItem = originalSetItem;
      localStorage.removeItem = originalRemoveItem;
      localStorage.clear = originalClear;
    };
  }, []);

    function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    localStorage.removeItem("id");
    navigate("/login");
  }
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [showPersonaPicker, setShowPersonaPicker] = useState(false);
  const [showPersonaCreate, setShowPersonaCreate] = useState(false);
  const [showPersonaCreatedPopup, setShowPersonaCreatedPopup] = useState(false);
  const [isCreatingChat, setIsCreatingChat] = useState(false);
  const [personas, setPersonas] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [deleteMode, setDeleteMode] = useState(false);
  const [showPersonaDeletedPopup, setShowPersonaDeletedPopup] = useState(false);
  const [showConfirmDeletePersona, setShowConfirmDeletePersona] = useState(false);
  const [personaToDelete, setPersonaToDelete] = useState(null);

  // Combined initialization effect - load personas and conversations together
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const storedUsername = localStorage.getItem("username");
    const interviewerId = localStorage.getItem("id");
    
    // Check auth first
    if (!token || !interviewerId) {
      navigate("/login");
      return;
    }
    
    setUsername(storedUsername || "");
    
    let mounted = true;

    async function loadInitialData() {
      setIsLoading(true);
      
      try {
        // Load both personas and conversations in parallel
        const [personasData, conversationsData] = await Promise.all([
          fetchAllPersonas(),
          fetchConversations(interviewerId)
        ]);
        
        if (!mounted) return;
        
        // Handle personas
        const personasArray = personasData?.items || [];
        console.log("Fetched personas:", personasData);
        console.log("Personas array:", personasArray);
        setPersonas(personasArray);
        
        // Handle conversations
        const convList = conversationsData || [];
        setConversations(convList);
        
        if (convList.length > 0) {
          const sorted = [...convList].sort((a, b) => {
            const ta = new Date(a.created_at || a.updated_at || 0).getTime();
            const tb = new Date(b.created_at || b.updated_at || 0).getTime();
            return tb - ta;
          });
          setCurrentSessionId(sorted[0].session_id);
          setShowPersonaPicker(false);
        } else {
          setShowPersonaPicker(true);
          setCurrentSessionId(null);
          setCurrentConversation(null);
          setSelectedPersona(null);
        }
      } catch (err) {
        console.error("Erro ao carregar dados iniciais:", err);
        
        if (err.message.includes("401") || err.message.includes("Unauthorized")) {
          console.log("Authentication failed, redirecting to login");
          navigate("/login");
          return;
        }
        
        if (mounted) {
          setPersonas([]);
          setConversations([]);
          setShowPersonaPicker(true);
          setCurrentSessionId(null);
          setCurrentConversation(null);
          setSelectedPersona(null);
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    }

    loadInitialData();
    return () => { mounted = false; };
  }, [navigate]);

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

  function handleDeleteClick() {
    setDeleteMode(!deleteMode);
  }

  async function handlePersonaDelete(persona) {
    if (!persona || !persona.id) {
      console.error("Invalid persona for deletion");
      return;
    }

    setPersonaToDelete(persona);
    setShowConfirmDeletePersona(true);
  }

  async function confirmPersonaDeletion() {
    if (!personaToDelete) return;

    try {
      // First, find and delete all conversations with this persona
      const conversationsToDelete = conversations.filter(
        conv => conv.persona?.toLowerCase() === personaToDelete.name?.toLowerCase()
      );
      
      console.log(`Deleting ${conversationsToDelete.length} conversations for persona ${personaToDelete.name}`);
      
      // Delete all conversations associated with this persona
      await Promise.all(
        conversationsToDelete.map(conv => 
          deleteConversationBySessionId(conv.session_id).catch(err => {
            console.error(`Error deleting conversation ${conv.session_id}:`, err);
          })
        )
      );
      
      // Then delete the persona
      await deletePersonaById(personaToDelete.id);
      
      // Refresh the personas list
      const data = await fetchAllPersonas();
      const personasArray = data?.items || [];
      setPersonas(personasArray);
      
      // Refresh the conversations list
      const interviewerId = localStorage.getItem("id");
      let updatedList = [];
      
      try {
        updatedList = await fetchConversations(interviewerId);
      } catch (err) {
        console.error("Error fetching conversations after persona deletion:", err);
        // If error is 404 or any fetch error, treat as no conversations
        if (err.message.includes("404") || err.message.includes("Failed to fetch")) {
          updatedList = [];
        }
      }
      
      // Update conversations state
      setConversations(updatedList);
      
      // Handle UI state based on remaining conversations
      if (updatedList.length === 0) {
        // No conversations left, show persona picker
        setCurrentSessionId(null);
        setCurrentConversation(null);
        setSelectedPersona(null);
        setShowPersonaPicker(true);
      } else {
        // Check if current conversation was deleted
        const currentConvDeleted = conversationsToDelete.some(
          conv => conv.session_id === currentSessionId
        );
        
        if (currentConvDeleted) {
          // Select the first remaining conversation
          const sorted = [...updatedList].sort((a, b) => {
            const ta = new Date(a.created_at || a.updated_at || 0).getTime();
            const tb = new Date(b.created_at || b.updated_at || 0).getTime();
            return tb - ta;
          });
          setCurrentSessionId(sorted[0].session_id);
          setSelectedPersona(sorted[0].persona);
          setShowPersonaPicker(false);
        }
      }
      
      setDeleteMode(false);

      // Show success message
      setShowPersonaDeletedPopup(true);
      setTimeout(() => setShowPersonaDeletedPopup(false), 2000);
    } catch (err) {
      console.error("Error deleting persona:", err);
      alert("Erro ao excluir persona: " + err.message);
    } finally {
      setShowConfirmDeletePersona(false);
      setPersonaToDelete(null);
    }
  }

  function cancelPersonaDeletion() {
    setShowConfirmDeletePersona(false);
    setPersonaToDelete(null);
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
      {showPersonaDeletedPopup && (
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
          Persona apagada com sucesso!
        </div>
      )}
      {showConfirmDeletePersona && (
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
            onClick={cancelPersonaDeletion}
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
                Apagar persona "{personaToDelete?.name}"?
              </h3>
              <p style={{ margin: "0 0 24px 0", color: "#666", fontSize: "1rem" }}>
                Esta ação não pode ser desfeita.
              </p>
              <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
                <button
                  onClick={cancelPersonaDeletion}
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
                  Cancelar
                </button>
                <button
                  onClick={confirmPersonaDeletion}
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
                  Apagar
                </button>
              </div>
            </div>
          </div>
        </>
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
                    deleteMode={deleteMode}
                    onDeleteClick={handleDeleteClick}
                    onPersonaDelete={handlePersonaDelete}
                  />
                  {conversations.length > 0 && (
                    <button
                      className="new-chat-btn persona-cancel-btn"
                      style={{ marginTop: "32px" }}
                      onClick={() => {
                        setShowPersonaPicker(false);
                        setDeleteMode(false);
                      }}
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
