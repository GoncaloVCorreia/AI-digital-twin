# src/chatbot/rag_agent.py
import os
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI

# ==========================================
# 🔧 CONFIGURAÇÃO
# ==========================================
os.environ["GOOGLE_API_KEY"] = "AIzaSyCg5X640F9n7O25T8h2_3S3b-lPE6X1Wmg"  # substitui pelo teu

DB_PATH = "data/chroma_theses"
COLLECTION = "thesis_docs"

# ==========================================
# ⚙️ MODELOS
# ==========================================
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# ==========================================
# 🧱 BASE DE DADOS CHROMA
# ==========================================
# Se não existir, cria com alguns docs de exemplo
if not os.path.exists(DB_PATH):
    print("🚀 Criar base Chroma com documentos de teste...")
    docs = [
        Document(
            page_content="A tese de Rafael Ferreira aborda o uso de agentes multi-inteligência em aplicações de software colaborativas.",
            metadata={"source": "Tese Rafael 2024"}
        ),
        Document(
            page_content="O relatório final discute a avaliação de desempenho de modelos de linguagem de grande escala (LLMs).",
            metadata={"source": "Relatório Final 2024"}
        ),
        Document(
            page_content="A dissertação explora métodos de integração de RAG (Retrieval-Augmented Generation) em sistemas académicos.",
            metadata={"source": "Dissertação 2025"}
        ),
    ]
    Chroma.from_documents(
        docs,
        embedding=embeddings,
        collection_name=COLLECTION,
        persist_directory=DB_PATH
    )

vectorstore = Chroma(
    collection_name=COLLECTION,
    embedding_function=embeddings,
    persist_directory=DB_PATH
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# ==========================================
# 🤖 FUNÇÃO PRINCIPAL DO AGENTE
# ==========================================
def thesis_rag_agent(query: str) -> str:
    docs = retriever.invoke(query)

    if not docs:
        return "Não encontrei documentos relevantes para essa questão."

    context = "\n\n---\n\n".join([
        f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
        for doc in docs
    ])

    prompt = f"""
    You are an academic assistant. Use the following thesis or report documents
    to answer the question clearly and accurately.

    Question: {query}

    Documents:
    {context}

    Answer in Portuguese:
    """

    response = llm.invoke(prompt)
    return response.content.strip()

# ==========================================
# 🧪 TESTE LOCAL
# ==========================================
if __name__ == "__main__":
    print("🔍 Teste rápido ao agente RAG")
    question = "Do que trata a dissertação sobre RAG?"
    print(f"\n❓ Pergunta: {question}")
    answer = thesis_rag_agent(question)
    print("\n💬 Resposta:")
    print(answer)
