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

export async function deleteConversationBySessionId(sessionId) {
  const response = await fetch(
    `${BASE_URL}/conversations/delete/${sessionId}`,
    {
      method: "DELETE",
      headers: {  
        ...getAuthHeader(),
        "Content-Type": "application/json",
      },
    }
  );
  if (!response.ok) throw new Error("Erro ao apagar conversa");
  return await response.json();
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

export async function createNewPersona(name,age,location,description,education,tech_skills,soft_skills,strenghts,weaknesses,goals,hobbies,personality) {
  const response = await fetch(`http://127.0.0.1:8000/personas`, {
    method: "POST",
    headers: {
      ...getAuthHeader(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name,
      age,  
      location,
      description,
      education,
      tech_skills,
      soft_skills,
      strenghts,
      weaknesses,
      goals,
      hobbies,
      personality
    }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Erro ao criar nova persona");
  }
  return await response.json();
}

export async function fetchAllPersonas() {
  const response = await fetch(`http://127.0.0.1:8000/personas`, {
    method: "GET",
    headers: {
      ...getAuthHeader(),
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) throw new Error("Erro ao buscar personas");
  return await response.json();
}