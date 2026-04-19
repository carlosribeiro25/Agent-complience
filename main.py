# from crew import ComplienceCrew
# from dotenv import load_dotenv
# import time

# load_dotenv(override=True)


# def run_complience_assistant(pergunta: str):
#     t0 = time.time()
#     crew_instance = ComplienceCrew()

#     result = crew_instance.crew().kickoff(inputs={"pergunta": pergunta})

#     print(f"Tempo total: {time.time() - t0:.2f}s")
#     return result


from crew import ComplienceCrew
from dotenv import load_dotenv
import time

load_dotenv(override=True)


def build_agent():
    """
    Inicializa a CrewAI uma única vez.
    Chamado pelo @st.cache_resource no app.py — não executa a cada pergunta.
    """
    crew_instance = ComplienceCrew()
    return crew_instance.crew()


def run_complience_assistant(pergunta: str, crew=None):
    """
    Executa o agente com a pergunta recebida.
    Se 'crew' for passado (vindo do cache), reutiliza o objeto já criado.
    Se não for passado, cria um novo (compatibilidade com chamadas diretas).
    """
    t0 = time.time()

    if crew is None:
        crew = build_agent()

    result = crew.kickoff(inputs={"pergunta": pergunta})

    print(f"Tempo total: {time.time() - t0:.2f}s")
    return str(result)