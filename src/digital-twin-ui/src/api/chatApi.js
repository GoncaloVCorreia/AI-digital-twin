const BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

function getAuthHeader() {
  // Force a fresh read every time
  const token = localStorage.getItem("access_token");
  
  if (!token) {
    console.warn("⚠️ getAuthHeader called but no token found!");
    console.trace(); // Show where this was called from
  }
  
  console.log("🔑 Using token for API call:", token ? `${token.substring(0, 20)}...` : "NO TOKEN");
  
  return {
    Authorization: `Bearer ${token || ""}`,
  };
}

export async function fetchConversations(interviewerId) {
  console.log("📞 Fetching conversations for interviewer:", interviewerId);
  const response = await fetch(
    `${BASE_URL}/chat/conversations/by-interviewer/${interviewerId}`,
    {
      headers: {
        ...getAuthHeader(),
      },
    }
  );
  console.log("📥 Fetch conversations response status:", response.status);
  if (!response.ok) {
    if (response.status === 401) {
      console.error("❌ 401 Unauthorized - Token invalid or expired");
      throw new Error("401 Unauthorized - Authentication failed");
    }
    throw new Error("Erro ao carregar conversas");
  }
  return response.json();
}

export async function fetchConversationBySessionId(sessionId) {
  console.log("📞 Fetching conversation by session:", sessionId);
  try {
    const res = await fetch(`${BASE_URL}/chat/conversations/by-session/${sessionId}`,
    {
      headers: {
        ...getAuthHeader(),
      },
    }
    );
    console.log("📥 Fetch conversation response status:", res.status);
    if (!res.ok) {
      if (res.status === 401) {
        console.error("❌ 401 Unauthorized - Token invalid or expired");
        throw new Error("401 Unauthorized - Authentication failed");
      }
      throw new Error("Erro ao buscar conversa");
    }
    return await res.json();
  } catch (err) {
    console.error(err);
    throw err;
  }
}

export async function deleteConversationBySessionId(sessionId) {
  const response = await fetch(
    `${BASE_URL}/chat/conversations/delete/${sessionId}`,
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
  console.log("📞 Sending message to API:", { sessionId, persona, message });
  const response = await fetch(`${BASE_URL}/chat/respond`, {
    method: "POST",
    headers: {
      ...getAuthHeader(), 
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      persona: persona,
      session_id: sessionId,
      messages: [
        { role: "system", content: "Be concise." },
        { role: "user", content: message },
      ],
    }),
  });
  console.log("📥 Send message response status:", response.status);

  if (!response.ok) {
    if (response.status === 401) {
      console.error("❌ 401 Unauthorized - Token invalid or expired");
      throw new Error("401 Unauthorized - Authentication failed");
    }
    throw new Error("Erro ao enviar mensagem");
  }
  return await response.json();
}

export async function createNewPersona(name,age,location,description,education,tech_skills,soft_skills,strenghts,weaknesses,goals,hobbies,personality,data_path) {
  const response = await fetch(`${BASE_URL}/personas`, {
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
      personality,
      data_path
    }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Erro ao criar nova persona");
  }
  return await response.json();
}

export async function fetchAllPersonas() {
  console.log("📞 Fetching all personas");
  const response = await fetch(`${BASE_URL}/personas`, {
    method: "GET",
    headers: {
      ...getAuthHeader(),
      "Content-Type": "application/json",
    },
  });
  console.log("📥 Fetch personas response status:", response.status);
  if (!response.ok) {
    if (response.status === 401) {
      console.error("❌ 401 Unauthorized - Token invalid or expired");
      throw new Error("401 Unauthorized - Authentication failed");
    }
    throw new Error("Erro ao buscar personas");
  }
  return await response.json();
}

export async function deletePersonaById(personaId) {
  console.log("📞 Deleting persona:", personaId);
  const response = await fetch(
    `${BASE_URL}/personas/${personaId}`,
    {
      method: "DELETE",
      headers: {  
        ...getAuthHeader(),
        "Content-Type": "application/json",
      },
    }
  );
  console.log("📥 Delete persona response status:", response.status);
  if (!response.ok) throw new Error("Erro ao apagar persona");
  
  // Handle empty response (204 No Content)
  const text = await response.text();
  return text ? JSON.parse(text) : { success: true };
}