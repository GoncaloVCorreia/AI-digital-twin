// Temporary mock backend simulation

// add mock conversations to simulate prior chats
const mockConversations = [
  {
    id: "conv1",
    otherUserName: "Rafael",
    lastMessage: "Até logo!",
    messages: [
      { role: "other", text: "Olá! Como estás?" },
      { role: "user", text: "Bem, obrigado." },
      { role: "other", text: "Até logo!" },
    ],
  },
  {
    id: "conv2",
    otherUserName: "Maria",
    lastMessage: "Obrigado pelo feedback.",
    messages: [
      { role: "other", text: "Olá, revisei o protótipo." },
      { role: "user", text: "Ótimo — obrigado!" },
      { role: "other", text: "Obrigado pelo feedback." },
    ],
  },
  {
    id: "conv3",
    otherUserName: "Joao",
    lastMessage: "Vou agendar para amanhã.",
    messages: [
      { role: "other", text: "Preciso dos dados para o relatório." },
      { role: "user", text: "Enviei por e-mail." },
      { role: "other", text: "Vou agendar para amanhã." },
    ],
  },
];

// fetch list of conversations (lightweight metadata)
export async function fetchConversations() {
  await new Promise((res) => setTimeout(res, 300));
  // return shallow copy to simulate network transfer
  return mockConversations.map((c) => ({
    id: c.id,
    otherUserName: c.otherUserName,
    lastMessage: c.lastMessage,
  }));
}

// fetch full conversation by id
export async function fetchConversationById(id) {
  await new Promise((res) => setTimeout(res, 300));
  const conv = mockConversations.find((c) => c.id === id);
  return conv ? JSON.parse(JSON.stringify(conv)) : null; // return deep copy
}

// topic: existing sendMessageToMockAPI kept and unchanged but exported earlier
export async function sendMessageToMockAPI(message, persona) {
  await new Promise((res) => setTimeout(res, 700)); // simulate delay

  const mockReplies = {
    rafael: "Olá! Sou o Rafael, estudante de IA apaixonado por criar sistemas inteligentes.",
    maria: "Sou a Maria, especialista em UX e comunicação digital.",
    joao: "Chamo-me João e foco-me em data science e automação.",
    ana: "Sou a Ana, desenvolvedora backend com gosto por resolver problemas complexos.",
  };

  const reply = mockReplies[persona?.toLowerCase()] || "Prazer! Sou o Digital Twin do grupo.";
  return { reply };
}
