from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
import os

# Ruta de los PDFs
PDF_DIR = "./data"

# Ruta donde se guardará la BD vectorial
CHROMA_DIR = "./chroma_db"

def load_documents(pdf_dir):
    documents = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            path = os.path.join(pdf_dir, filename)
            loader = PyPDFLoader(path)
            documents.extend(loader.load())
    return documents

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_documents(documents)

def embed_and_store(docs, persist_directory):
    embedding_function = OllamaEmbeddings(model="nomic-embed-text")
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embedding_function,
        persist_directory=persist_directory
    )
    vectordb.persist()
    return vectordb

if __name__ == "__main__":
    print("📚 Cargando documentos PDF...")
    docs = load_documents(PDF_DIR)
    print(f"✅ {len(docs)} documentos cargados.")

    print("✂️ Dividiendo en fragmentos...")
    chunks = split_documents(docs)
    print(f"✅ {len(chunks)} fragmentos generados.")

    print("🧠 Generando embeddings y almacenando en ChromaDB...")
    embed_and_store(chunks, CHROMA_DIR)
    print("✅ Proceso completado.")


def procesar_documentos(pdf_dir="./data", persist_dir="./chroma_db"):
    print("📚 Cargando documentos PDF...")
    docs = load_documents(pdf_dir)
    print(f"✅ {len(docs)} documentos cargados.")

    print("✂️ Dividiendo en fragmentos...")
    chunks = split_documents(docs)
    print(f"✅ {len(chunks)} fragmentos generados.")

    print("🧠 Generando embeddings y almacenando en ChromaDB...")
    embed_and_store(chunks, persist_dir)
    print("✅ Proceso completado.")

    return len(docs), len(chunks)

