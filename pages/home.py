import streamlit as st
import time

# Configuração inicial da página
st.set_page_config(page_title="Playground", layout="wide")

# Inicialização das variáveis de estado
if 'mostrar_logs' not in st.session_state:
    st.session_state.mostrar_logs = False
if 'opcoes_assist' not in st.session_state:
    st.session_state.opcoes_assist = ["Padrão"]
if 'selecao_atual' not in st.session_state:
    st.session_state.selecao_atual = "Padrão"
if 'confirmar_delecao' not in st.session_state:
    st.session_state.confirmar_delecao = False

# Funções auxiliares
def atualizar_nome():
    if st.session_state.novo_nome and st.session_state.novo_nome not in st.session_state.opcoes_assist:
        st.session_state.opcoes_assist.append(st.session_state.novo_nome)
        st.session_state.selecao_atual = st.session_state.novo_nome

def atualizar_nome_existente():
    if st.session_state.nome_editado and st.session_state.nome_editado != assist:
        idx = st.session_state.opcoes_assist.index(assist)
        st.session_state.opcoes_assist[idx] = st.session_state.nome_editado
        st.session_state.selecao_atual = st.session_state.nome_editado

# Estilo CSS personalizado
st.markdown("""
    <style>
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
    </style>
""", unsafe_allow_html=True)

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
                    st.session_state.opcoes_assist.remove(assist)
                    st.session_state.selecao_atual = "Padrão"
                    st.session_state.confirmar_delecao = False
                    st.rerun()
            with col2:
                if st.button("Não", key=f"nao_{assist}"):
                    st.session_state.confirmar_delecao = False
                    st.rerun()

    # Interface de edição do nome
    st.subheader("Nome")
    if assist == "Adicionar novo assistente":
        novo_nome = st.text_input("Nome do assistente", key="novo_nome", on_change=atualizar_nome)
    else:
        nome_editado = st.text_input("Nome do assistente", value=assist, key="nome_editado", on_change=atualizar_nome_existente)

    # Configurações do assistente
    st.subheader("Sistema")
    sistema_msg = st.text_area("Mensagem do sistema", "Você é um assistente prestativo, criativo e honesto.")

    st.subheader("Modelo")
    modelo = st.selectbox("Selecione o modelo", ["GPT-4", "GPT-3.5", "GPT-3"])
    
    st.subheader("Parâmetros")
    temperatura = st.slider("Temperatura", 0.0, 2.0, 1.0, 0.01)
    top_p = st.slider("Top P", 0.0, 1.0, 1.0, 0.01)
    tokens_max = st.slider("Tokens máximos", 1, 4000, 2000)

# Coluna principal
with col_principal:
    # Cabeçalho
    col_titulo, col_botao = st.columns([5,1])
    with col_titulo:
        st.title("Playground")
    with col_botao:
        st.button('Logs', key='toggle_logs', on_click=lambda: setattr(st.session_state, 'mostrar_logs', not st.session_state.mostrar_logs))
    
    # Área de entrada e saída
    prompt = st.text_area("Digite seu prompt aqui", height=200, key="prompt")

    col1, col2, col3 = st.columns([1,1,5])
    with col1:
        enviar = st.button("Enviar")
        
    st.markdown("### Resposta")
    output_placeholder = st.empty()

    if enviar:
        with st.spinner("Gerando resposta..."):
            time.sleep(2)
            resposta = "Esta é uma resposta simulada do ChatGPT. Em uma implementação real, aqui seria integrada a API do OpenAI para gerar respostas reais."
            with output_placeholder:
                st.markdown(f"""
                <div class="output-box">
                    {resposta}
                </div>
                """, unsafe_allow_html=True)

    # Informações de status
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Tokens usados:** 0/2000")
    with col2:
        st.markdown("**Tempo de resposta:** 2s")
    with col3:
        st.markdown("**Modelo:** " + modelo)

# Coluna de logs
if st.session_state.mostrar_logs:
    with col_logs:
        st.title("Logs")
        st.write("Aqui você pode ver os logs do sistema")
        st.write("Histórico de interações")
        st.write("Estatísticas de uso")

