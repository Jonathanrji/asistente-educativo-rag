from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory

def crear_memoria_conversacional():
    """
    Inicializa una memoria conversacional en sesión para mantener el historial.
    """
    history = StreamlitChatMessageHistory(key="chat_history")
    memory = ConversationBufferMemory(
        chat_memory=history,
        return_messages=True,
        memory_key="chat_history"
    )
    return memory
