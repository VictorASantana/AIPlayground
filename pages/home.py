import streamlit as st
import time
from streamlit_modal import Modal
from streamlit_chat import message
from services.file_storage import delete_file, save_file, delete_all_files
from services.assistant_storage import create_assistant, get_assistant, get_all_assistants, update_assistant, delete_assistant
import openai

from services.text_processing import retrieve_information, store_in_faiss
from utils.file_processing import extract_text_from_pdf, extract_text_from_txt

# Configuração inicial da página
st.set_page_config(page_title="Instituto Minerva Playground", initial_sidebar_state="collapsed", layout="wide")

params = st.query_params

if "redirected" not in st.session_state:
    st.session_state["redirected"] = True
    st.switch_page("main.py")  # Change to the actual page path

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Inicialização das variáveis de estado
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

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'file_content' not in st.session_state:
    st.session_state.file_content = []
if 'file_names' not in st.session_state:
    st.session_state.file_names = []

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
    /* Estilo para o botão de upload de arquivos */
    button[data-testid="baseButton-secondary"] {
        visibility: hidden;
        position: relative;
    }
    button[data-testid="baseButton-secondary"]::after {
        content: "Anexar arquivo";
        visibility: visible;
        position: absolute;
        left: 0;
        right: 0;
    }
    /* Hide file uploader instructions */
    [data-testid="stFileDropzoneInstructions"] {
        display: none;
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

col_menu, col_principal = st.columns([1.2, 4])

# Coluna de menu
with col_menu:
    st.title("Assistente")

    assistants = get_all_assistants()
    st.session_state.opcoes_assist = ["Padrão"] + [a["name"] for a in assistants]
    # Criar mapeamento de nome para ID
    st.session_state.assistants_map = {a["name"]: a["id"] for a in assistants}
    st.session_state.assistants_loaded = True
    
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
                    "gpt-4o-mini-2024-07-18"
                ],
                key="modelo",
                on_change=on_model_change)
    
    st.slider("Temperatura", 
              0.0, 1.5,
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
    col_titulo, col_limpar, col_upload, col_remove = st.columns([4, 1, 1, 1])
    
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
            label="Upload a file", 
            type=['txt', 'pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'ico', 'webp', 'docx', 'doc', 'xls', 'xlsx', 'ppt', 'pptx'], 
            key=f"file_uploader_{st.session_state['uploaded_file_counter']}", 
            label_visibility="collapsed"
        ) 

        modal = Modal("Arquivos carregados", key="file_modal", padding=20)

        if st.button("Arquivos Carregados"):
            modal.open()

    with col_remove:
        remove_file = st.button("Remover arquivos", key="remover_arquivo")
      

    chat_container = st.container()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    # Exibir mensagens usando streamlit-chat
    with chat_container:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                message(msg["content"], is_user=True, key=str(i))
            else:
                assistant_name = msg.get("assistant_name", st.session_state.selecao_atual)
                message(f"**{assistant_name}:** {msg['content']}", is_user=False, key=str(i))

    # Input do usuário usando callback
    def on_input_change():
        user_input = st.session_state.user_input
        query = st.session_state.user_input
        if len(st.session_state.uploaded_files) > 0:
            st.session_state.file_content = []
            for content in st.session_state.uploaded_files:
                vectorstore = store_in_faiss(content)
                st.session_state.file_content.append(vectorstore)
            
            context = " | ".join(map(lambda x: retrieve_information(query, x), st.session_state.file_content))
            user_input = f"Use as informações a seguir para responder:\n{context}\n\nPergunta: {user_input} (considere os textos separados por '|' como pertencentes a arquivos diferentes)"
        if user_input:
            # Adicionar mensagem do usuário ao histórico
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Criar um placeholder para a resposta e medir o tempo
            start_time = time.time()
            #with st.spinner('Gerando resposta...'):
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

            response_time = time.time() - start_time
            
            # Capturar informações de uso de tokens
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            # Atualizar o contador de tokens na session state
            if 'total_tokens' not in st.session_state:
                st.session_state.total_tokens = 0
            st.session_state.total_tokens = total_tokens

            st.session_state.messages.pop()
            st.session_state.messages.append({"role": "user", "content": query})
            # Adicionar resposta ao histórico com informações de tokens
            st.session_state.messages.append({
                "role": "assistant", 
                "content": assistant_response,
                "response_time": response_time,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "assistant_name": st.session_state.selecao_atual
            })
            
            # Atualizar o tempo de resposta mais recente
            st.session_state.last_response_time = response_time
            
            # Limpar o input
            st.session_state.user_input = ""

    st.text_input("Digite sua mensagem:", key="user_input", on_change=on_input_change)

    if modal.is_open():
        with modal.container():
            st.write("Arquivos adicionados")
            files_to_remove = []
            for i, file in enumerate(st.session_state.uploaded_files):
                col1, col2 = st.columns([4,2])
                col1.write(f"📄 {st.session_state.file_names[i]}")
                if col2.button("❌", key=f"remove_{i}"):
                    files_to_remove.append(i)

            for i in sorted(files_to_remove, reverse=True):
                del st.session_state.uploaded_files[i]
                delete_file(st.session_state.file_names[i])
                del st.session_state.file_names[i]
                st.rerun()

    # Processar o arquivo carregado
    if uploaded_file is not None:
        st.markdown('''
            <style>
                .uploadedFile {display: none}
            <style>''',
            unsafe_allow_html=True
            )
        start_time = time.time()
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'txt':
            try:
                file_content = extract_text_from_txt(uploaded_file)
                save_file(
                    agent_id=st.session_state.id_atual,
                    file_name=uploaded_file.name,
                    file_data=file_content.encode('utf-8')
                )

                st.success("Arquivo processado e indexado")
                st.session_state.uploaded_files.append(file_content)
                st.session_state.file_names.append(uploaded_file.name)

                # Incrementar contador do file uploader para resetar
                st.session_state["uploaded_file_counter"] += 1
                st.rerun()
            except UnicodeDecodeError:
                file_content = "Please provide utf-8 encoded text."
        elif file_extension == 'pdf':
            file_content = extract_text_from_pdf(uploaded_file)
            save_file(
                agent_id=st.session_state.id_atual,
                file_name=uploaded_file.name,
                file_data=file_content.encode('utf-8')
            )

            st.success("Arquivo processado e indexado")
            st.session_state.uploaded_files.append(file_content)
            st.session_state.file_names.append(uploaded_file.name)

            # Incrementar contador do file uploader para resetar
            st.session_state["uploaded_file_counter"] += 1
            st.rerun()
        else: 
            st.toast(":red[Por favor, adicione um arquivo e formato compatível (.pdf ou .txt)]")
            st.session_state["uploaded_file_counter"] += 1
            st.rerun()
            
        

    if remove_file:
        delete_all_files(st.session_state.id_atual)
        response = f"Deleted files from agent {st.session_state.id_atual}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": time.time()
        })
        st.session_state["file_content"] = ''
        st.rerun()
    # Informações de status
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if 'total_tokens' in st.session_state:
            st.markdown(f"**Tokens usados:** {st.session_state.total_tokens}/{st.session_state.current_max_tokens}")
        else:
            st.markdown(f"**Tokens usados:** 0/{st.session_state.current_max_tokens}")
    with col2:
        if 'last_response_time' in st.session_state:
            st.markdown(f"**Tempo de resposta:** {st.session_state.last_response_time:.2f}s")
        else:
            st.markdown("**Tempo de resposta:** -")
    with col3:
        st.markdown("**Modelo:** " + st.session_state.current_model)
