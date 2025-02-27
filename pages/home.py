import streamlit as st
import time
import random
from streamlit_chat import message
from services.file_storage import save_file, delete_file
from services.assistant_storage import create_assistant, get_assistant, get_all_assistants, update_assistant, delete_assistant
import openai

# Configuração inicial da página
st.set_page_config(page_title="Playground", initial_sidebar_state="collapsed", layout="wide")

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Inicialização das variáveis de estado
if 'mostrar_logs' not in st.session_state:
    st.session_state.mostrar_logs = False
if 'opcoes_assist' not in st.session_state:
    st.session_state.opcoes_assist = ["Padrão"]
if 'selecao_atual' not in st.session_state:
    st.session_state.selecao_atual = "Padrão"
if 'id_atual' not in st.session_state:
    st.session_state.id_atual = 1
if 'ids' not in st.session_state:
    st.session_state.ids = []

if 'confirmar_delecao' not in st.session_state:
    st.session_state.confirmar_delecao = False
if 'assistants_map' not in st.session_state:
    st.session_state.assistants_map = {}

# Inicializar variáveis de configuração
if 'current_model' not in st.session_state:
    st.session_state.current_model = "chatgpt-4o-latest"
if 'current_temperature' not in st.session_state:
    st.session_state.current_temperature = 1.0
if 'current_top_p' not in st.session_state:
    st.session_state.current_top_p = 1.0
if 'current_max_tokens' not in st.session_state:
    st.session_state.current_max_tokens = 2000
if 'current_system_msg' not in st.session_state:
    st.session_state.current_system_msg = "Você é um assistente prestativo, criativo e honesto."

# Inicializar variáveis temporárias para os campos de edição
if 'sistema_msg' not in st.session_state:
    st.session_state.sistema_msg = st.session_state.current_system_msg
if 'modelo' not in st.session_state:
    st.session_state.modelo = st.session_state.current_model
if 'temperatura' not in st.session_state:
    st.session_state.temperatura = st.session_state.current_temperature
if 'top_p' not in st.session_state:
    st.session_state.top_p = st.session_state.current_top_p
if 'tokens_max' not in st.session_state:
    st.session_state.tokens_max = st.session_state.current_max_tokens

if 'openai_model' not in st.session_state:
    st.session_state.openai_model = "chatgpt-4o-latest"
if 'openai_temperature' not in st.session_state:
    st.session_state.openai_temperature = 1.0
if 'openai_top_p' not in st.session_state:
    st.session_state.openai_top_p = 1.0
if 'openai_max_tokens' not in st.session_state:
    st.session_state.openai_max_tokens = 2000

# Funções auxiliares
def atualizar_nome():
    if st.session_state.novo_nome and st.session_state.novo_nome not in st.session_state.opcoes_assist:
        # Criar novo assistente no banco
        assistant_id = create_assistant(
            name=st.session_state.novo_nome,
            system_message="Você é um assistente prestativo, criativo e honesto.",
            model="chatgpt-4o-latest",
            temperature=1.0,
            top_p=1.0,
            max_tokens=2000
        )
        st.session_state.opcoes_assist.append(st.session_state.novo_nome)
        st.session_state.selecao_atual = st.session_state.novo_nome

        st.session_state.id_atual = assistant_id
        #st.session_state.id_atual = random.randint(100, 1000)
        st.session_state.ids.append(st.session_state.id_atual)


def atualizar_nome_existente():
    if st.session_state.nome_editado and st.session_state.nome_editado != assist:
        # Atualizar o nome no banco de dados
        update_assistant(
            assistant_id=st.session_state.id_atual,
            name=st.session_state.nome_editado,
            system_message=st.session_state.current_system_msg,
            model=st.session_state.current_model,
            temperature=st.session_state.current_temperature,
            top_p=st.session_state.current_top_p,
            max_tokens=st.session_state.current_max_tokens
        )
        
        # Atualizar o nome na interface
        idx = st.session_state.opcoes_assist.index(assist)
        st.session_state.opcoes_assist[idx] = st.session_state.nome_editado
        st.session_state.selecao_atual = st.session_state.nome_editado
        
        # Atualizar o mapeamento de nomes para IDs
        st.session_state.assistants_map[st.session_state.nome_editado] = st.session_state.id_atual
        if assist in st.session_state.assistants_map:
            del st.session_state.assistants_map[assist]

# Estilo CSS personalizado
css = """<style>
    .main {
        padding: 0rem 1rem;
    }
    .stTextArea textarea {
        height: 200px;
    }
    .output-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 4px;
        min-height: 200px;
    }
    /* Removendo os estilos gerais da coluna e aplicando apenas à coluna de logs */
    [data-testid="stSidebarNav"] {
        max-height: 80vh;
        overflow-y: auto;
    }
    
    /* Estilizando a barra de rolagem apenas para a coluna de logs */
    [data-testid="stSidebarNav"]::-webkit-scrollbar {
        width: 10px;
    }
    
    [data-testid="stSidebarNav"]::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 5px;
    }
    
    [data-testid="stSidebarNav"]::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 5px;
    }
    
    [data-testid="stSidebarNav"]::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    /* Estilizando o upload de arquivos */
    [data-testid='stFileUploader'] {
        width: max-content;
    }
    [data-testid='stFileUploader'] section {
        padding: 0;
        float: left;
    }
    [data-testid='stFileUploader'] section > input + div {
        display: none;
    }
    [data-testid='stFileUploader'] section + div {
        float: right;
        padding-top: 0;
    }
    /* Estilo para o botão de logout */
    div[data-testid="column"]:last-child {
        display: flex;
        justify-content: flex-end;
        align-items: center;
    }
    div[data-testid="column"]:last-child button {
        width: auto;
    }
    </style>
"""
st.markdown(css, unsafe_allow_html=True)

# Header with email and logout
display_email, _, logout_button = st.columns([6, 3, 1])
with display_email:
    st.title(f"Bem-vindo, {st.session_state.user_info.get('email')}")
with logout_button:
    if st.button("Voltar", use_container_width=True):
        st.switch_page("main.py")

# Definição do layout principal
if st.session_state.mostrar_logs:
    col_menu, col_principal, col_logs = st.columns([1.2, 3, 1])
else:
    col_menu, col_principal = st.columns([1.2, 4])

# Coluna de menu
with col_menu:
    st.title("Assistente")
    
    # Seleção do assistente
    opcoes_display = st.session_state.opcoes_assist + ["Adicionar novo assistente"]
    assist = st.selectbox("Selecione o assistente", opcoes_display, index=opcoes_display.index(st.session_state.selecao_atual))

    # Atualizar o ID atual e carregar configurações quando um assistente é selecionado
    if assist == "Adicionar novo assistente":
        # Resetar para valores padrão
        st.session_state.current_system_msg = "Você é um assistente prestativo, criativo e honesto."
        st.session_state.current_model = "chatgpt-4o-latest"
        st.session_state.current_temperature = 1.0
        st.session_state.current_top_p = 1.0
        st.session_state.current_max_tokens = 2000
        
        # Atualizar valores dos widgets
        st.session_state.sistema_msg = "Você é um assistente prestativo, criativo e honesto."
        st.session_state.modelo = "chatgpt-4o-latest"
        st.session_state.temperatura = 1.0
        st.session_state.top_p = 1.0
        st.session_state.tokens_max = 2000

        # Atualizar valores da API OpenAI
        st.session_state.openai_model = "chatgpt-4o-latest"
        st.session_state.openai_temperature = 1.0
        st.session_state.openai_top_p = 1.0
        st.session_state.openai_max_tokens = 2000

    elif assist != "Adicionar novo assistente":
        if assist != "Padrão":
            # Atualizar ID atual
            st.session_state.id_atual = st.session_state.assistants_map.get(assist, 1)
            st.session_state.selecao_atual = assist
            
            # Carregar configurações do banco
            assistant_data = get_assistant(st.session_state.id_atual)
            if assistant_data:
                # Atualizar valores atuais
                st.session_state.current_system_msg = assistant_data["system_message"]
                st.session_state.current_model = assistant_data["model"]
                st.session_state.current_temperature = float(assistant_data["temperature"])
                st.session_state.current_top_p = float(assistant_data["top_p"])
                st.session_state.current_max_tokens = int(assistant_data["max_tokens"])
                
                # Atualizar valores dos widgets
                st.session_state.sistema_msg = assistant_data["system_message"]
                st.session_state.modelo = assistant_data["model"]
                st.session_state.temperatura = float(assistant_data["temperature"])
                st.session_state.top_p = float(assistant_data["top_p"])
                st.session_state.tokens_max = int(assistant_data["max_tokens"])

                # Atualizar valores da API OpenAI
                st.session_state.openai_model = assistant_data["model"]
                st.session_state.openai_temperature = float(assistant_data["temperature"])
                st.session_state.openai_top_p = float(assistant_data["top_p"])
                st.session_state.openai_max_tokens = int(assistant_data["max_tokens"])
        else:
            # Configurações padrão
            st.session_state.id_atual = 1
            st.session_state.selecao_atual = "Padrão"
            
            # Atualizar valores atuais
            st.session_state.current_system_msg = "Você é um assistente prestativo, criativo e honesto."
            st.session_state.current_model = "chatgpt-4o-latest"
            st.session_state.current_temperature = 1.0
            st.session_state.current_top_p = 1.0
            st.session_state.current_max_tokens = 2000
            
            # Atualizar valores dos widgets
            st.session_state.sistema_msg = "Você é um assistente prestativo, criativo e honesto."
            st.session_state.modelo = "chatgpt-4o-latest"
            st.session_state.temperatura = 1.0
            st.session_state.top_p = 1.0
            st.session_state.tokens_max = 2000

            # Atualizar valores da API OpenAI
            st.session_state.openai_model = "chatgpt-4o-latest"
            st.session_state.openai_temperature = 1.0
            st.session_state.openai_top_p = 1.0
            st.session_state.openai_max_tokens = 2000

    # Interface de edição do nome
    st.subheader("Nome")
    if assist == "Adicionar novo assistente":
        novo_nome = st.text_input("Nome do assistente", key="novo_nome", on_change=atualizar_nome)
    else:
        nome_editado = st.text_input("Nome do assistente", value=assist, key="nome_editado", on_change=atualizar_nome_existente)

    # Mostrar campos de configuração sempre
    def on_system_msg_change():
        if assist != "Padrão" and assist != "Adicionar novo assistente":
            update_assistant(
                assistant_id=st.session_state.id_atual,
                name=assist,
                system_message=st.session_state.sistema_msg,
                model=st.session_state.current_model,
                temperature=st.session_state.current_temperature,
                top_p=st.session_state.current_top_p,
                max_tokens=st.session_state.current_max_tokens
            )
            st.session_state.current_system_msg = st.session_state.sistema_msg

    def on_model_change():
        if assist != "Padrão" and assist != "Adicionar novo assistente":
            update_assistant(
                assistant_id=st.session_state.id_atual,
                name=assist,
                system_message=st.session_state.current_system_msg,
                model=st.session_state.modelo,
                temperature=st.session_state.current_temperature,
                top_p=st.session_state.current_top_p,
                max_tokens=st.session_state.current_max_tokens
            )
            st.session_state.current_model = st.session_state.modelo
        st.session_state.openai_model = st.session_state.modelo

    def on_temperature_change():
        if assist != "Padrão" and assist != "Adicionar novo assistente":
            update_assistant(
                assistant_id=st.session_state.id_atual,
                name=assist,
                system_message=st.session_state.current_system_msg,
                model=st.session_state.current_model,
                temperature=st.session_state.temperatura,
                top_p=st.session_state.current_top_p,
                max_tokens=st.session_state.current_max_tokens
            )
            st.session_state.current_temperature = st.session_state.temperatura
        st.session_state.openai_temperature = st.session_state.temperatura

    def on_top_p_change():
        if assist != "Padrão" and assist != "Adicionar novo assistente":
            update_assistant(
                assistant_id=st.session_state.id_atual,
                name=assist,
                system_message=st.session_state.current_system_msg,
                model=st.session_state.current_model,
                temperature=st.session_state.current_temperature,
                top_p=st.session_state.top_p,
                max_tokens=st.session_state.current_max_tokens
            )
            st.session_state.current_top_p = st.session_state.top_p
        st.session_state.openai_top_p = st.session_state.top_p

    def on_max_tokens_change():
        if assist != "Padrão" and assist != "Adicionar novo assistente":
            update_assistant(
                assistant_id=st.session_state.id_atual,
                name=assist,
                system_message=st.session_state.current_system_msg,
                model=st.session_state.current_model,
                temperature=st.session_state.current_temperature,
                top_p=st.session_state.current_top_p,
                max_tokens=st.session_state.tokens_max
            )
            st.session_state.current_max_tokens = st.session_state.tokens_max
        st.session_state.openai_max_tokens = st.session_state.tokens_max

    # Atualizar os valores temporários quando o assistente muda
    if st.session_state.selecao_atual != assist:
        st.session_state.sistema_msg = st.session_state.current_system_msg
        st.session_state.modelo = st.session_state.current_model
        st.session_state.temperatura = st.session_state.current_temperature
        st.session_state.top_p = st.session_state.current_top_p
        st.session_state.tokens_max = st.session_state.current_max_tokens

    st.text_area("Mensagem do sistema", 
                key="sistema_msg",
                on_change=on_system_msg_change)
    
    st.selectbox("Selecione o modelo", 
                [
                    "gpt-4o",
                    "gpt-4o-2024-08-06",
                    "chatgpt-4o-latest",
                    "gpt-4o-mini",
                    "gpt-4o-mini-2024-07-18",
                    "o1",
                    "o1-2024-12-17",
                    "o1-mini",
                    "o1-mini-2024-09-12",
                    "o3-mini",
                    "o3-mini-2025-01-31",
                    "o1-preview",
                    "o1-preview-2024-09-12",
                    "gpt-4o-realtime-preview",
                    "gpt-4o-realtime-preview-2024-12-17",
                    "gpt-4o-mini-realtime-preview",
                    "gpt-4o-mini-realtime-preview-2024-12-17"
                ],
                key="modelo",
                on_change=on_model_change)
    
    st.slider("Temperatura", 
              0.0, 2.0,
              step=0.01,
              key="temperatura",
              on_change=on_temperature_change)
    
    st.slider("Top P",
              0.0, 1.0,
              step=0.01,
              key="top_p",
              on_change=on_top_p_change)
    
    st.slider("Tokens máximos",
              1, 4000,
              key="tokens_max",
              on_change=on_max_tokens_change)

    # Interface de exclusão do assistente
    if assist != "Adicionar novo assistente" and assist != "Padrão":
        deletar_key = f"deletar_{assist}"
        if st.button("🗑️ Excluir assistente", key=deletar_key):
            st.session_state.confirmar_delecao = True
            
        if st.session_state.confirmar_delecao:
            st.warning(f"Tem certeza que deseja excluir o assistente '{assist}'?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Sim", key=f"sim_{assist}"):
                    delete_assistant(st.session_state.id_atual)
                    st.session_state.opcoes_assist.remove(assist)
                    st.session_state.selecao_atual = "Padrão"
                    st.session_state.confirmar_delecao = False
                    st.rerun()
            with col2:
                if st.button("Não", key=f"nao_{assist}"):
                    st.session_state.confirmar_delecao = False
                    st.rerun()

# Coluna principal
with col_principal:
    # Cabeçalho
    col_titulo, col_limpar, col_upload, col_remove, col_botoes = st.columns([4, 1, 1, 1, 1])
    
    with col_titulo:
        st.title(f"Playground")

    with col_limpar:
        if st.button("Limpar thread", key="limpar_thread"):
            st.session_state.messages = []
            st.rerun()
        
    with col_upload:
        if "uploaded_file_counter" not in st.session_state:
            st.session_state["uploaded_file_counter"] = 1

        uploaded_file = st.file_uploader(
            "Upload File", 
            type=['txt', 'pdf', 'docx'], 
            key=f"file_uploader_{st.session_state['uploaded_file_counter']}", 
            label_visibility="collapsed"
        )

    with col_remove:
        remove_file = st.button("Remover arquivos", key="remover_arquivo")
      
    with col_botoes:
        if "mostrar_logs" not in st.session_state:
            st.session_state.mostrar_logs = False
        
        st.button('Logs', key='toggle_logs', on_click=lambda: setattr(st.session_state, 'mostrar_logs', not st.session_state.mostrar_logs))

    chat_container = st.container()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    # Exibir mensagens usando streamlit-chat
    with chat_container:
        for i, msg in enumerate(st.session_state.messages):
            message(msg["content"], is_user=(msg["role"] == "user"), key=str(i))

    # Input do usuário usando callback
    def on_input_change():
        user_input = st.session_state.user_input
        if user_input:
            # Adicionar mensagem do usuário ao histórico
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Criar um placeholder para a resposta
            with st.spinner('Gerando resposta...'):
                response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": "system", "content": st.session_state.current_system_msg},
                        *[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.messages]
                    ],
                    temperature=st.session_state["openai_temperature"],
                    top_p=st.session_state["openai_top_p"],
                    max_tokens=st.session_state["openai_max_tokens"]
                )
                assistant_response = response.choices[0].message.content

            # Adicionar resposta ao histórico
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
            # Limpar o input
            st.session_state.user_input = ""
            #st.rerun()

    st.text_input("Digite sua mensagem:", key="user_input", on_change=on_input_change)

    # Processar o arquivo carregado
    if uploaded_file is not None:
        start_time = time.time()
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'txt':
            try:
                file_content = uploaded_file.read().decode('utf-8')
                save_file(
                    agent_id=st.session_state.id_atual,
                    file_name=uploaded_file.name,
                    file_data=file_content.encode('utf-8')
                )
            except UnicodeDecodeError:
                file_content = "Please provide utf-8 encoded text."
        else:
            file_content = f"File '{uploaded_file.name}' uploaded successfully. Binary content not displayed."
        
        end_time = time.time()
        
        response = f"Received file: {uploaded_file.name}\n\nContent:\n{file_content}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": time.time(),
            "tokens": len(str(file_content).split()),
            "response_time": end_time - start_time
        })
        
        # Incrementar contador do file uploader para resetar
        st.session_state["uploaded_file_counter"] += 1
        st.rerun()

    if remove_file:
        delete_file(st.session_state.id_atual)
        response = f"Deleted files from agent {st.session_state.id_atual}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": time.time()
        })
        st.rerun()
    # Informações de status
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Tokens usados:** 0/{st.session_state.current_max_tokens}")
    with col2:
        st.markdown("**Tempo de resposta:** 2s")
    with col3:
        st.markdown("**Modelo:** " + st.session_state.current_model)

# Coluna de logs
if st.session_state.mostrar_logs:
    with col_logs:
        st.title("Logs")
        st.write("Aqui você pode ver os logs do sistema")
        st.write("Histórico de interações")
        st.write("Estatísticas de uso")

# Carregar assistentes ao iniciar
if 'assistants_loaded' not in st.session_state:
    assistants = get_all_assistants()
    st.session_state.opcoes_assist = ["Padrão"] + [a["name"] for a in assistants]
    # Criar mapeamento de nome para ID
    st.session_state.assistants_map = {a["name"]: a["id"] for a in assistants}
    st.session_state.assistants_loaded = True