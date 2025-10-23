# src/chatbot/rag_agent.py
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
import os

os.environ["GOOGLE_API_KEY"] = "AIzaSyCg5X640F9n7O25T8h2_3S3b-lPE6X1Wmg"

# 1. Define LLM e Embeddings
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Carrega Chroma existente (ou cria nova se ainda não existir)
DB_PATH = "data/chroma_theses"
vectorstore = Chroma(
    collection_name="thesis_docs",
    embedding_function=embeddings,
    persist_directory=DB_PATH
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 3. Função principal RAG
def thesis_rag_agent(query: str) -> str:
    docs = retriever.invoke(query)

    context = "\n\n---\n\n".join([
        f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
        for doc in docs
    ])

    prompt = f"""
    You are an academic assistant. Use the following thesis/report documents
    to answer the question. Be specific and cite sources if possible.

    Question: {query}

    Documents:
    {context}

    Answer:
    """

    response = llm.invoke(prompt)
    return response.content
