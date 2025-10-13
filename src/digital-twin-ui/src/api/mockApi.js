// Temporary mock backend simulation
export async function sendMessageToMockAPI(message, persona) {
  await new Promise((res) => setTimeout(res, 700)); // simulate delay

  const mockReplies = {
    rafael: "Olá! Sou o Rafael, estudante de IA apaixonado por criar sistemas inteligentes.",
    maria: "Sou a Maria, especialista em UX e comunicação digital.",
    joao: "Chamo-me João e foco-me em data science e automação.",
    ana: "Sou a Ana, desenvolvedora backend com gosto por resolver problemas complexos.",
  };

  const reply = mockReplies[persona.toLowerCase()] || "Prazer! Sou o Digital Twin do grupo.";
  return { reply };
}
