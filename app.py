from dotenv import load_dotenv

load_dotenv(override=True)

import streamlit as st
from main import run_complience_assistant

st.title("Assistent de estudos")
st.write(
    " no estudo das leis da intituição"
)

with st.sidebar:
    st.header("Descreva uma terefa:")
    tipo_tarefa = "Responder pergunta sober a contituição"

    pergunta_usuario = st.text_area("Digite sua pergunta.")

if st.button("Executar verificação"):
    if not pergunta_usuario.strip():
        st.warning("Por favor, digite sua pergunta antes de excutar.")
    else: 
        st.write("Processando sua pergunta...")

    resultado = run_complience_assistant(pergunta_usuario)

    st.subheader('Resposta do Agente')
    st.write(resultado)