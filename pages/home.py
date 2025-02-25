import streamlit as st
import time

# Configurar layout wide no início do script
# Hide the sidebar menu and set wide layout
st.set_page_config(initial_sidebar_state="collapsed", layout="wide")

# Criar cinco colunas (incluindo espaços)
col1, space1, col2, space2, col3 = st.columns([60, 20, 60, 20, 60])

# Adicionar os títulos em cada coluna
with col1:
    st.title("Lista de agentes")
    agentes = ["Agente 1", "Agente 2", "Agente 3"]
    agente_selecionado = st.selectbox("Lista de agentes", agentes)
    subcol1_1, subcol1_2 = st.columns(2)
    with subcol1_1:
        st.button(f"Excluir {agente_selecionado}", key=f"excluir_{agente_selecionado}")
    with subcol1_2:
        st.button("Novo agente", key="novo_agente")

    st.subheader("Configurações do agente selecionado")
    modelos = ["modelo 1", "modelo 2", "modelo 3"]
    modelos_selecionado = st.selectbox("Lista de modelos", modelos)
    #st.slider("Temperatura", min_value=1, max_value=10, value=1)
    #st.slider("Top P", min_value=1, max_value=10, value=1)
    #st.slider("Max tokens", min_value=1, max_value=10, value=1)
    st.session_state.temperatura = st.slider("Temperatura", min_value=1, max_value=10, value=1)
    st.session_state.top_p = st.slider("Top P", min_value=1, max_value=10, value=1)
    st.session_state.max_tokens = st.slider("Max tokens", min_value=1, max_value=10, value=1)

with col2:
    st.title("Thread")  # Threads de cada agente

    if "uploaded_file" not in st.session_state:
        st.session_state["uploaded_file"] = 1

    uploaded_file = st.file_uploader("Choose a file", type=['txt', 'pdf', 'docx'], key=st.session_state["uploaded_file"], label_visibility="visible")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if uploaded_file is not None:
        # Read file content based on file type
        start_time = time.time()
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'txt':
            # For text files, decode as UTF-8
            try:
                file_content = uploaded_file.read().decode('utf-8')
            except UnicodeDecodeError:
                file_content = f"Please provide utf-8 encoded text."
        else:
            # For binary files (PDF, DOCX, etc.), just acknowledge the upload
            file_content = f"File '{uploaded_file.name}' uploaded successfully. Binary content not displayed."
        
        end_time = time.time()
        #Add file content to messages
        response = f"Received file: {uploaded_file.name}\n\nContent:\n{file_content}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": time.time(),
            "tokens": len(str(file_content).split()),  # Simple token count estimation
            "response_time": end_time - start_time
        })
        
        # Clear the file uploader
        st.session_state["uploaded_file"] += 1
        st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input("Digite sua mensagem aqui")
    if user_message:
        # Add timestamp and metadata to message
        start_time = time.time()
        
        st.session_state.messages.append({
            "role": "user",
            "content": user_message,
            "timestamp": time.time(),
            "tokens": len(user_message.split())  # Simple token count estimation
        })
        
        # Simulate API response
        response = f"Resposta {len(st.session_state.messages)//2} do agente"
        end_time = time.time()
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": time.time(),
            "tokens": len(response.split()),  # Simple token count estimation
            "response_time": end_time - start_time
        })
        st.rerun()

    cleart_button = st.button("Limpar thread", key=f"limpar_thread_{agente_selecionado}")
    if cleart_button:
        st.session_state.messages = []
        st.rerun()

with col3:
    st.title("Logs")  # Logs de cada agente
    
    # Display logs for each interaction
    for i in range(0, len(st.session_state.messages), 2):
        with st.expander(f"Interação {i//2 + 1}", expanded=True):
            # User message info
            st.markdown("**Mensagem do usuário:**")
            st.markdown(f"- Tokens: {st.session_state.messages[i].get('tokens', 0)}")
            
            # Assistant response info
            if i + 1 < len(st.session_state.messages):
                st.markdown("**Resposta do assistente:**")
                st.markdown(f"- Tokens: {st.session_state.messages[i+1].get('tokens', 0)}")
                st.markdown(f"- Tempo de resposta: {st.session_state.messages[i+1].get('response_time', 0):.2f}s")
                
            # Model parameters
            st.markdown("**Parâmetros do modelo:**")
            st.markdown(f"- Modelo: {modelos_selecionado}")
            st.markdown(f"- Temperatura: {st.session_state.temperatura if 'temperatura' in st.session_state else 1}")
            st.markdown(f"- Top P: {st.session_state.top_p if 'top_p' in st.session_state else 1}")
            st.markdown(f"- Max tokens: {st.session_state.max_tokens if 'max_tokens' in st.session_state else 1}")
            
            st.divider()








