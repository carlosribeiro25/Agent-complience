from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from main import build_agent, run_complience_assistant
from historico import carregar_historico, salvar_entrada, limpar_historico

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Assistente de Estudos",
    page_icon="⚖️",
    layout="centered",
)

@st.cache_resource(show_spinner=False)
def get_agent():
   
    return build_agent()


# ── Cache de respostas já consultadas (evita re-execução da mesma pergunta) ──
@st.cache_data(show_spinner=False, ttl=3600)
def responder_com_cache(pergunta: str) -> str:
    crew = get_agent()
    return run_complience_assistant(pergunta, crew=crew)


# ── Persistent history: carrega do disco uma vez por sessão ──────────────────
if "historico" not in st.session_state:
    st.session_state.historico = carregar_historico()

if "ultima_resposta" not in st.session_state:
    st.session_state.ultima_resposta = None

if "ultima_pergunta" not in st.session_state:
    st.session_state.ultima_pergunta = None

# ── Custom CSS (dark-mode-aware) ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    :root {
        --accent:        #1a6fc4;
        --accent-light:  #e8f0fb;
        --text-primary:  #1a1a2e;
        --text-secondary:#4a5568;
        --bg-card:       #ffffff;
        --border:        #e2e8f0;
    }
    [data-theme="dark"] {
        --accent:        #60a5fa;
        --accent-light:  #1e3a5f;
        --text-primary:  #e2e8f0;
        --text-secondary:#a0aec0;
        --bg-card:       #1e2533;
        --border:        #2d3748;
    }
    html, body, [class*="css"] { font-family: 'Georgia', 'Times New Roman', serif; }

    .app-header { text-align: center; padding: 2rem 0 1rem; }
    .app-header h1 { font-size: 2rem; font-weight: 700; color: var(--accent); margin-bottom: .25rem; }
    .app-header p  { color: var(--text-secondary); font-size: .95rem; margin: 0; }

    .answer-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent);
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        margin-top: 1rem;
        color: var(--text-primary);
        line-height: 1.75;
        font-size: 1rem;
    }
    .answer-label {
        font-size: .75rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: .08em; color: var(--accent); margin-bottom: .6rem;
    }
    .question-badge {
        background: var(--accent-light); border-radius: 6px;
        padding: .6rem 1rem; color: var(--text-primary);
        font-style: italic; font-size: .95rem; margin-bottom: .5rem;
    }
    .hist-item {
        border-left: 3px solid var(--accent); padding-left: .75rem;
        margin-bottom: .5rem; color: var(--text-primary);
    }
    [data-testid="stSidebar"] { border-right: 1px solid var(--border); }
    div[data-testid="stButton"] > button {
        background: var(--accent); color: #fff; border: none;
        border-radius: 6px; padding: .5rem 1.5rem;
        font-weight: 600; width: 100%; transition: opacity .2s;
    }
    div[data-testid="stButton"] > button:hover { opacity: .85; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
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

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 Sua tarefa")
    st.caption("Tarefa atual")
    st.info("Responder pergunta baseado na constituição", icon="📜")
    st.divider()

    pergunta_usuario = st.text_area(
        "✏️ Digite sua pergunta",
        placeholder="Ex: Quais são os direitos fundamentais garantidos pela Constituição?",
        height=160,
    )
    executar = st.button("🔍 Executar verificação")

    st.divider()
    st.caption("💡 Dica: seja específico para obter respostas mais precisas.")

    # ── Histórico persistido ──────────────────────────────────────────────────
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

# ── Área principal ────────────────────────────────────────────────────────────
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

        # Tenta streaming se o agente expuser o método stream()
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
            # Fallback: usa cache para evitar recalcular a mesma pergunta
            with st.spinner("Consultando a constituição…"):
                full_response = responder_com_cache(pergunta_usuario)

        # Renderização final sem cursor piscando
        placeholder.markdown(
            f'<div class="answer-card">'
            f'<div class="answer-label">⚖️ Resposta do Agente</div>'
            f'{full_response}</div>',
            unsafe_allow_html=True,
        )

        # Persiste no disco e atualiza session_state
        salvar_entrada(pergunta_usuario, full_response)
        st.session_state.historico = carregar_historico()
        st.session_state.ultima_pergunta = pergunta_usuario
        st.session_state.ultima_resposta = full_response

        with st.expander("📄 Ver resposta em texto simples"):
            st.text(full_response)

        st.success("Consulta concluída com sucesso!", icon="✅")

# Exibe a última resposta da sessão mesmo após rerun (ex: ao limpar histórico)
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
                Digite sulabela pergunta na barra lateral e clique em
                <strong>Executar verificação</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )