from crew import ComplienceCrew
from dotenv import load_dotenv
import time

load_dotenv(override=True)

def run_complience_assistant(pergunta: str):
    t0 = time.time()
    crew_instance = ComplienceCrew()

    result = crew_instance.crew().kickoff(inputs={"pergunta": pergunta})

    print(f"Tempo total: {time.time() - t0:.2f}s")
    return result


