from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from main import build_agent, run_complience_assistant
from historico import carregar_historico, salvar_entrada, limpar_historico
import re
from tools import extrair_questao_estruturada, carregar_gabarito

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

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_acertou" not in st.session_state:
    st.session_state.quiz_acertou = False

from pathlib import Path

@st.cache_data(show_spinner=False)
def load_css():
    return Path("styles/main.css").read_text()

st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="app-header">
        <h1>⚖️ Assistente de Estudos</h1>
        <p>Tire suas dúvidas sobre a Constituição Federal e pratique com o Simulado BNB</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.divider()

with st.sidebar:
    st.markdown("## 📋 Sua tarefa")
    st.caption("Tarefa atual")
    st.info("Responder perguntas referente a Constituição Federal ou questões do Simulado BNB.")
    st.divider()

    pergunta_usuario = st.text_area(
        "Digite sua pergunta",
        placeholder="Ex: Quais são os direitos fundamentais? ou qual é a questão 5 do simulado BNB?",
        height=160,
    )
    executar = st.button("Executar verificação")

    st.divider()
    st.caption("💡 Dica: para o simulado, peça pelo número da questão. Ex: 'questão 10 do simulado BNB'"
    "")

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
        num_questao = re.search(r"(?:quest[\u00e3a]o|pergunta)\s*(\d{1,2})", pergunta_usuario, re.IGNORECASE)
        num_questao = int(num_questao.group(1)) if num_questao and 1 <= int(num_questao.group(1)) <= 70 else None

        if num_questao is not None:
            with st.spinner("Carregando quest\u00e3o do simulado..."):
                dados = extrair_questao_estruturada(num_questao)
            if dados:
                st.session_state.quiz = dados
                st.session_state.quiz_acertou = False
                st.session_state.ultima_resposta = None
                st.session_state.ultima_pergunta = pergunta_usuario
                st.rerun()
            else:
                st.error(f"N\u00e3o foi poss\u00edvel extrair a quest\u00e3o {num_questao} do simulado.")
        else:
            st.session_state.quiz = None
            st.markdown(
                f'<div class="question-badge">🗣️ <strong>Pergunta:</strong> {pergunta_usuario}</div>',
                unsafe_allow_html=True,
            )

            placeholder = st.empty()
            full_response = ""

            crew = get_agent()

            if callable(getattr(crew, "stream", None)):
                with st.spinner("Consultando\u2026"):
                    for chunk in crew.stream({"pergunta": pergunta_usuario}):
                        full_response += chunk
                        placeholder.markdown(
                            f'<div class="answer-card">'
                            f'<div class="answer-label">\u2696\ufe0f Resposta do Agente</div>'
                            f'{full_response}\u258c</div>',
                            unsafe_allow_html=True,
                        )
            else:
                with st.spinner("Consultando\u2026"):
                    full_response = responder_com_cache(pergunta_usuario)

            placeholder.markdown(
                f'<div class="answer-card">'
                f'<div class="answer-label">\u2696\ufe0f Resposta do Agente</div>'
                f'{full_response}</div>',
                unsafe_allow_html=True,
            )

            salvar_entrada(pergunta_usuario, full_response)
            st.session_state.historico = carregar_historico()
            st.session_state.ultima_pergunta = pergunta_usuario
            st.session_state.ultima_resposta = full_response

            with st.expander("📄 Ver resposta em texto simples"):
                st.text(full_response)

            st.success("Consulta conclu\u00edda com sucesso!", icon="\u2705")

# --- Quiz interativo do Simulado ---
if st.session_state.quiz is not None:
    quiz = st.session_state.quiz

    st.markdown(f"### 📝 Questão {quiz['numero']}")
    st.markdown(f"**📌 Assunto:** {quiz['assunto']}")
    st.divider()

    if st.session_state.quiz_acertou:
        st.markdown(quiz["enunciado"])
        st.divider()
        for letra, texto in quiz["alternativas"].items():
            st.markdown(f"**({letra})** {texto}")
        st.success("🎉 Resposta correta! Parabéns!", icon="✅")
    else:
        st.markdown(quiz["enunciado"])
        st.divider()

        opcoes = [f"({k}) {v}" for k, v in quiz["alternativas"].items()]
        escolha = st.radio(
            "Selecione sua resposta:",
            opcoes,
            index=None,
            key=f"quiz_escolha_{quiz['numero']}",
        )

        confirmar = st.button("✅ Confirmar resposta")

        if confirmar:
            if escolha is None:
                st.warning("⚠️ Selecione uma alternativa antes de confirmar.")
            else:
                letra = escolha[1]
                gabarito = carregar_gabarito()
                correta = gabarito.get(str(quiz["numero"]))
                if correta is None:
                    st.warning("⚠️ Gabarito não configurado para esta questão. Preencha o arquivo gabarito.json.")
                elif letra == correta:
                    st.session_state.quiz_acertou = True
                    st.rerun()
                else:
                    st.error("❌ Resposta incorreta! Tente novamente.")

elif not executar and st.session_state.ultima_resposta:
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

elif not executar:
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