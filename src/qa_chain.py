from langchain_community.vectorstores import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain, LLMChain, StuffDocumentsChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

CHROMA_DIR = "./chroma_db"

def load_vectorstore():
    embedding = OllamaEmbeddings(model="nomic-embed-text")
    vectordb = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedding
    )
    return vectordb

def build_rag_chain(modelo="llama3"):
    vectordb = load_vectorstore()
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    llm = Ollama(
        model=modelo,
        temperature=0.2,
        num_predict=300
    )

    # Prompt personalizado para responder
    prompt_template = """
Eres un asistente educativo. Usa solo la información proporcionada en los textos siguientes para responder de forma clara, concisa y en español.

Contexto:
{context}

Pregunta:
{question}

Respuesta:"""
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    combine_docs_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context"
    )

    # Prompt para generar la reformulación de preguntas (obligatorio aunque no se use mucho)
    question_prompt = PromptTemplate.from_template("Reformula esta conversación y pregunta para recuperación: {chat_history} {question}")
    question_generator = LLMChain(llm=llm, prompt=question_prompt)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"  # 👈 Esto evita el error de ambigüedad
    )


    rag_chain = ConversationalRetrievalChain(
        retriever=retriever,
        memory=memory,
        combine_docs_chain=combine_docs_chain,
        question_generator=question_generator,
        return_source_documents=True
    )



    return rag_chain
