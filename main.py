from crew import ComplienceCrew
from dotenv import load_dotenv

load_dotenv(override=True)

def run_complience_assistant(pergunta: str):
    crew_instance = ComplienceCrew()

    result = crew_instance.crew().kickoff(inputs={"pergunta": pergunta})

    return result

