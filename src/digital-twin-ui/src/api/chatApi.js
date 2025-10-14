const BASE_URL = "http://127.0.0.1:8000/chat";

function getAuthHeader() {
  const token = localStorage.getItem("access_token");
  return {
    Authorization: `Bearer ${token}`,
  };
}

export async function fetchConversations(interviewerId) {
  const response = await fetch(
    `${BASE_URL}/conversations/by-interviewer/${interviewerId}`,
    {
      headers: {
        ...getAuthHeader(),
      },
    }
  );
  if (!response.ok) throw new Error("Erro ao carregar conversas");
  return response.json();
}

export async function fetchConversationBySessionId(sessionId) {
  try {
    // http://127.0.0.1:8000/chat/conversations/by-session/session-8fd2c0b75633
    const res = await fetch(`${BASE_URL}/conversations/by-session/${sessionId}`,
    {
      headers: {
        ...getAuthHeader(),
      },
    }
    );
    if (!res.ok) throw new Error("Erro ao buscar conversa");
    return await res.json();
  } catch (err) {
    console.error(err);
    return null;
  }
}

export async function sendMessageToAPI(sessionId, persona, message) {
  console.log("Sending message to API:", { sessionId, persona, message });
  const response = await fetch(`${BASE_URL}/respond`, {
    method: "POST",
    headers: {
      ...getAuthHeader(), 
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      persona: persona,
      session_id: sessionId,
      messages: [ // <-- fix key name
        { role: "system", content: "Be concise." }, // <-- non-empty system prompt
        { role: "user", content: message },
      ],
    }),
  });
  console.log("API response status:", response.status);

  if (!response.ok) throw new Error("Erro ao enviar mensagem");
  return await response.json();
}
