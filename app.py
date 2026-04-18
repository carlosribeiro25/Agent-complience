from dotenv import load_dotenv

load_dotenv(override=True)

import streamlit as st
from main import run_complience_assistant

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Assistente de Estudos",
    page_icon="⚖️",
    layout="centered",
)

# ── Custom CSS (dark-mode-aware) ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ---------- tokens ---------- */
    :root {
        --accent:        #1a6fc4;
        --accent-light:  #e8f0fb;
        --text-primary:  #1a1a2e;
        --text-secondary:#4a5568;
        --bg-card:       #ffffff;
        --border:        #e2e8f0;
        --success:       #276749;
        --success-bg:    #f0fff4;
    }

    /* Dark-mode overrides — Streamlit adds [data-theme="dark"] on <html> */
    [data-theme="dark"] {
        --accent:        #60a5fa;
        --accent-light:  #1e3a5f;
        --text-primary:  #e2e8f0;
        --text-secondary:#a0aec0;
        --bg-card:       #1e2533;
        --border:        #2d3748;
        --success:       #68d391;
        --success-bg:    #1a2e22;
    }

    /* ---------- global ---------- */
    html, body, [class*="css"] {
        font-family: 'Georgia', 'Times New Roman', serif;
    }

    /* ---------- header ---------- */
    .app-header {
        text-align: center;
        padding: 2rem 0 1rem;
    }
    .app-header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent);
        margin-bottom: .25rem;
    }
    .app-header p {
        color: var(--text-secondary);
        font-size: .95rem;
        margin: 0;
    }

    /* ---------- answer card ---------- */
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
    .answer-card .answer-label {
        font-size: .75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .08em;
        color: var(--accent);
        margin-bottom: .6rem;
    }

    /* ---------- question badge ---------- */
    .question-badge {
        background: var(--accent-light);
        border-radius: 6px;
        padding: .6rem 1rem;
        color: var(--text-primary);
        font-style: italic;
        font-size: .95rem;
        margin-bottom: .5rem;
    }

    /* ---------- sidebar ---------- */
    [data-testid="stSidebar"] {
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] h2 {
        color: var(--accent);
    }

    /* ---------- button ---------- */
    div[data-testid="stButton"] > button {
        background: var(--accent);
        color: #fff;
        border: none;
        border-radius: 6px;
        padding: .5rem 1.5rem;
        font-weight: 600;
        width: 100%;
        transition: opacity .2s;
    }
    div[data-testid="stButton"] > button:hover {
        opacity: .85;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ───────────────────────────────────────────────────────────────────
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

# ── Main area ─────────────────────────────────────────────────────────────────
if executar:
    if not pergunta_usuario.strip():
        st.warning("⚠️ Por favor, digite sua pergunta antes de executar.", icon="⚠️")
    else:
        # Show question recap
        st.markdown(
            f'<div class="question-badge">🗣️ <strong>Pergunta:</strong> {pergunta_usuario}</div>',
            unsafe_allow_html=True,
        )

        with st.spinner("Consultando a constituição…"):
            resultado = run_complience_assistant(pergunta_usuario)

        # Answer card
        st.markdown(
            f"""
            <div class="answer-card">
                <div class="answer-label">⚖️ Resposta do Agente</div>
                {resultado}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Expander with raw text (handy for copy-paste)
        with st.expander("📄 Ver resposta em texto simples"):
            st.text(resultado)

        st.success("Consulta concluída com sucesso!", icon="✅")
else:
    # Empty-state illustration
    st.markdown(
        """
        <div style="text-align:center; padding: 3rem 1rem; opacity: .55;">
            <div style="font-size:3rem;">📖</div>
            <p style="margin-top:.75rem; font-size:1rem;">
                Digite sua pergunta na barra lateral e clique em <strong>Executar verificação</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )