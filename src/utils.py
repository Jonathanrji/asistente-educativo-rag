from typing import List
from langchain.schema.document import Document

def mostrar_fuentes(documentos: List[Document]) -> str:
    """
    Recibe los documentos fuente y retorna una cadena formateada con las fuentes.
    """
    fuentes = []
    for doc in documentos:
        meta = doc.metadata
        fuente = meta.get("source", "desconocida")
        page = meta.get("page", None)
        if page is not None:
            fuentes.append(f"📄 {fuente}, página {page}")
        else:
            fuentes.append(f"📄 {fuente}")
    return "\n".join(set(fuentes))
