import { useState, useEffect } from "react";
import PersonaSelector from "../../components/PersonaSelector/PersonaSelector";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import ChatSidebar from "../../components/ChatWindow/ChatSidebar";
import { useNavigate } from "react-router-dom";
import "./ChatView.css";
import "../../styles.css";
import { fetchConversations, fetchConversationBySessionId} from "../../api/chatApi";

export default function ChatView() {
  const navigate = useNavigate();
  const username = localStorage.getItem("username");

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    navigate("/login");
  }

  const [selectedPersona, setSelectedPersona] = useState("Rafael");
  const [conversations, setConversations] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);

  // ✅ Fetch de todas as conversas reais do utilizador
  useEffect(() => {
    const interviewerId = 2; // por agora hardcoded
    let mounted = true;

    async function loadConversations() {
      try {
        const data = await fetchConversations(interviewerId);
        if (mounted) {
          setConversations(data);
          if (data.length > 0) setCurrentChatId(data[0].id);
          console.log("Conversations loaded:", data);
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
    // have to get session_id from conversations lists by currentChatId
    // then fetch by session_id
    if (!conversations || conversations.length === 0) return;
    const conv = conversations.find((c) => c.id === currentChatId);
    if (!conv) return;
    const { session_id } = conv;

    if (!currentChatId) {
      setCurrentConversation(null);
      return;
    }

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
  }, [currentChatId]);

  function onSelectConversation(id) {
    setCurrentChatId(id);
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
            <div className="right-panel">
              <aside className="persona-panel">
                <PersonaSelector
                  selected={selectedPersona}
                  setSelected={setSelectedPersona}
                />
              </aside>

              <div className="chat-area">
                <ChatWindow
                  persona={selectedPersona}
                  conversation={currentConversation}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Mantém sidebar à direita */}
        <ChatSidebar
          conversations={conversations}
          currentChatId={currentChatId}
          onSelectConversation={onSelectConversation}
        />
      </div>
    </div>
  );
}
