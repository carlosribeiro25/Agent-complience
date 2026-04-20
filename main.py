from crew import ComplienceCrew
from dotenv import load_dotenv
import time

load_dotenv(override=True)


def build_agent():  
    crew_instance = ComplienceCrew()
    return crew_instance.crew()

def run_complience_assistant(pergunta: str, crew=None):
    
    t0 = time.time()

    if crew is None:
        crew = build_agent()

    result = crew.kickoff(inputs={"pergunta": pergunta})

    print(f"Tempo total: {time.time() - t0:.2f}s")
    return str(result)