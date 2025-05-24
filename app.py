import streamlit as st
from src.qa_chain import build_rag_chain
from src.utils import mostrar_fuentes
from src.ingest import procesar_documentos
import os
import time
import shutil

# Configuración de la aplicación
st.set_page_config(page_title="Asistente Educativo RAG", page_icon="🧠")
st.title("🧠 Asistente Educativo RAG")
st.markdown("Haz preguntas sobre los documentos educativos cargados en PDF 📚")

# --- Estado inicial ---
ADMIN_PASS = "educa123"

if "es_admin" not in st.session_state:
    st.session_state.es_admin = False
if "accion_admin" not in st.session_state:
    st.session_state.accion_admin = None
if "accion_resultado" not in st.session_state:
    st.session_state.accion_resultado = None

# --- Ejecutar acciones diferidas (antes de interfaz) ---
if st.session_state.accion_admin == "reprocesar":
    with st.spinner("Procesando todos los documentos en /data..."):
        num_docs, num_chunks = procesar_documentos()
    st.session_state.accion_resultado = f"✅ Se procesaron {num_docs} documentos y {num_chunks} fragmentos."
    st.session_state.accion_admin = None
    st.rerun()

elif st.session_state.accion_admin == "limpiar":
    shutil.rmtree("chroma_db", ignore_errors=True)
    os.makedirs("chroma_db", exist_ok=True)

    # 💡 Limpiar la instancia del modelo RAG en memoria
    st.session_state.pop("qa_chain", None)
    st.session_state.pop("modelo_cargado", None)

    st.session_state.accion_resultado = "✅ Base de datos limpiada correctamente y reiniciada."
    st.session_state.accion_admin = None
    st.rerun()


elif st.session_state.accion_admin == "logout":
    st.session_state.es_admin = False
    st.session_state.accion_admin = None
    st.rerun()

# Mostrar resultado si existe
if st.session_state.accion_resultado:
    st.sidebar.success(st.session_state.accion_resultado)
    st.session_state.accion_resultado = None

# --- Autenticación administrador ---
st.sidebar.markdown("## 🔐 Modo Administrador")

if not st.session_state.es_admin:
    password = st.sidebar.text_input("Contraseña de administrador", type="password")
    if password == ADMIN_PASS:
        st.session_state.es_admin = True
        st.sidebar.success("🔓 Acceso concedido")
    elif password:
        st.sidebar.error("❌ Contraseña incorrecta")
else:
    st.sidebar.success("🔓 Modo administrador activo")

# --- Selección de modelo ---
st.sidebar.markdown("## 🤖 Modelo de lenguaje")
modelos_disponibles = {
    "llama3": "📘 LLaMA3: Preciso y reciente, ideal para respuestas contextuales.",
    "mistral": "📗 Mistral: Rápido y eficiente, ideal para uso general.",
    "deepseek-r1": "📕 DeepSeek: Bueno en razonamiento lógico y tareas educativas."
}
modelo_seleccionado = st.sidebar.selectbox(
    "Selecciona el modelo a usar:",
    list(modelos_disponibles.keys()),
    format_func=lambda k: f"{k} - {modelos_disponibles[k]}"
)
st.session_state.modelo = modelo_seleccionado

# --- Cargar modelo si es necesario ---
if "qa_chain" not in st.session_state or st.session_state.get("modelo_cargado") != st.session_state.modelo:
    st.session_state.qa_chain = build_rag_chain(modelo=st.session_state.modelo)
    st.session_state.modelo_cargado = st.session_state.modelo

# --- Inicializar historial visual ---
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# --- Funciones exclusivas del administrador ---
if st.session_state.es_admin:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📤 Subir nuevo PDF")

    if "uploaded_recently" not in st.session_state:
        st.session_state.uploaded_recently = False

    uploaded_file = st.sidebar.file_uploader("Selecciona un archivo PDF", type="pdf")

    if uploaded_file and not st.session_state.uploaded_recently:
        save_path = os.path.join("data", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success(f"✅ Archivo guardado: {uploaded_file.name}")
        st.session_state.uploaded_recently = True

        with st.spinner("📚 Procesando el nuevo documento..."):
            procesar_documentos()
        st.sidebar.success("🧠 Documento procesado e indexado correctamente.")
        st.rerun()

    if st.session_state.uploaded_recently and not uploaded_file:
        st.session_state.uploaded_recently = False

    st.sidebar.markdown("### 📥 Procesar todos los PDFs de /data")
    if st.sidebar.button("⚙️ Reprocesar carpeta /data"):
        st.session_state.accion_admin = "reprocesar"

    if st.sidebar.button("🧼 Limpiar base de datos Chroma"):
        st.session_state.accion_admin = "limpiar"

    if st.sidebar.button("🛑 Cerrar sesión admin"):
        st.session_state.accion_admin = "logout"

# --- Nueva conversación ---
if st.sidebar.button("🔁 Nueva conversación"):
    st.session_state.chat_log = []
    st.rerun()

# --- Entrada de usuario ---
prompt = st.chat_input("Haz una pregunta sobre los documentos...")

# Mostrar historial
for mensaje in st.session_state.chat_log:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# Procesar pregunta
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.chat_log.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            resultado = st.session_state.qa_chain.invoke({"question": prompt})
            fuentes_raw = resultado["source_documents"]
            respuesta = resultado["answer"]

            # Verificamos si no se recuperaron fuentes
            if not fuentes_raw:
                respuesta = "⚠️ No se encontró información en los documentos cargados para responder esta pregunta."

            fuentes = mostrar_fuentes(fuentes_raw)

            # Animación progresiva
            placeholder = st.empty()
            text = ""
            for palabra in respuesta.split():
                text += palabra + " "
                placeholder.markdown(text)
                time.sleep(0.03)

            if fuentes:
                with st.expander("📚 Ver fuentes"):
                    st.markdown(fuentes)

    st.session_state.chat_log.append({"role": "assistant", "content": respuesta})
