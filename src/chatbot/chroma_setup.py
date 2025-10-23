from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

docs = [
    Document(page_content="O relatório da Tese A discute o uso de LLMs em ambientes colaborativos...", metadata={"source": "Tese A"}),
    Document(page_content="A Tese B analisa o desempenho de redes neurais convolucionais em imagens médicas...", metadata={"source": "Tese B"}),
]
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
Chroma.from_documents(docs, embeddings, collection_name="thesis_docs", persist_directory="data/chroma_theses")
