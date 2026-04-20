from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from main import build_agent, run_complience_assistant
from historico import carregar_historico, salvar_entrada, limpar_historico

st.set_page_config(
    page_title="Assistente de Estudos",
    page_icon="⚖️",
    layout="centered",
)

@st.cache_resource(show_spinner=False)
def get_agent():
   
    return build_agent()

@st.cache_data(show_spinner=False, ttl=3600)
def responder_com_cache(pergunta: str) -> str:
    crew = get_agent()
    return run_complience_assistant(pergunta, crew=crew)

if "historico" not in st.session_state:
    st.session_state.historico = carregar_historico()

if "ultima_resposta" not in st.session_state:
    st.session_state.ultima_resposta = None

if "ultima_pergunta" not in st.session_state:
    st.session_state.ultima_pergunta = None

from pathlib import Path

@st.cache_data(show_spinner=False)
def load_css():
    return Path("styles/main.css").read_text()

st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="app-header">
        <h1>⚖️ Assistente de Estudos</h1>
        <p>Tire suas dúvidas sobre as leis da instituição</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.divider()

with st.sidebar:
    st.markdown("## 📋 Sua tarefa")
    st.caption("Tarefa atual")
    st.info("Responder pergunta baseado na constituição")
    st.divider()

    pergunta_usuario = st.text_area(
        "Digite sua pergunta",
        placeholder="Ex: Quais são os direitos fundamentais garantidos pela Constituição?",
        height=160,
    )
    executar = st.button("Executar verificação")

    st.divider()
    st.caption("💡 Dica: seja específico para obter respostas mais precisas.")

    if st.session_state.historico:
        st.divider()
        col1, col2 = st.columns([3, 1])
        col1.markdown("### 🕓 Histórico")
        if col2.button("🗑️", help="Limpar histórico"):
            limpar_historico()
            st.session_state.historico = []
            st.session_state.ultima_resposta = None
            st.session_state.ultima_pergunta = None
            st.rerun()

        for item in reversed(st.session_state.historico[-8:]):
            with st.expander(f"📌 {item['data']}"):
                st.markdown(
                    f'<div class="hist-item"><strong>Pergunta:</strong> {item["pergunta"]}</div>',
                    unsafe_allow_html=True,
                )
                st.write(item["resposta"])

if executar:
    if not pergunta_usuario.strip():
        st.warning("⚠️ Por favor, digite sua pergunta antes de executar.", icon="⚠️")
    else:
        st.markdown(
            f'<div class="question-badge">🗣️ <strong>Pergunta:</strong> {pergunta_usuario}</div>',
            unsafe_allow_html=True,
        )

        placeholder = st.empty()
        full_response = ""

        crew = get_agent()

        if callable(getattr(crew, "stream", None)):
            with st.spinner("Consultando a constituição…"):
                for chunk in crew.stream({"pergunta": pergunta_usuario}):
                    full_response += chunk
                    placeholder.markdown(
                        f'<div class="answer-card">'
                        f'<div class="answer-label">⚖️ Resposta do Agente</div>'
                        f'{full_response}▌</div>',
                        unsafe_allow_html=True,
                    )
        else:
            with st.spinner("Consultando a constituição…"):
                full_response = responder_com_cache(pergunta_usuario)

        placeholder.markdown(
            f'<div class="answer-card">'
            f'<div class="answer-label">⚖️ Resposta do Agente</div>'
            f'{full_response}</div>',
            unsafe_allow_html=True,
        )

        salvar_entrada(pergunta_usuario, full_response)
        st.session_state.historico = carregar_historico()
        st.session_state.ultima_pergunta = pergunta_usuario
        st.session_state.ultima_resposta = full_response

        with st.expander("📄 Ver resposta em texto simples"):
            st.text(full_response)

        st.success("Consulta concluída com sucesso!", icon="✅")

elif st.session_state.ultima_resposta:
    st.markdown(
        f'<div class="question-badge">🗣️ <strong>Pergunta:</strong> {st.session_state.ultima_pergunta}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="answer-card">'
        f'<div class="answer-">⚖️ Última resposta</div>'
        f'{st.session_state.ultima_resposta}</div>',
        unsafe_allow_html=True,
    )

else:
    st.markdown(
        """
        <div style="text-align:center; padding: 3rem 1rem; opacity: .55;">
            <div style="font-size:3rem;">📖</div>
            <p style="margin-top:.75rem; font-size:1rem;">
                Digite sua pergunta na barra lateral e clique em
                <strong>Executar verificação</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )