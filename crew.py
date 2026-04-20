
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource

load_dotenv(override=True)

@CrewBase
class ComplienceCrew:
    tasks_config = "config/tasks.yaml"
    agents_config = "config/agents.yaml"

    @agent
    def especialista_estudos(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_estudos"],
            verbose=False,
            tools=[],
            llm=LLM(model="gpt-5"),
        )

    @task
    def responder_perguntas(self) -> Task:
        return Task(
            config=self.tasks_config["responder_perguntas"],
            agent=self.especialista_estudos()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.especialista_estudos()],
            tasks=[
                self.responder_perguntas(),
            ],
            process=Process.sequential,
            verbose=False,
            knowledge_sources=[PDFKnowledgeSource(
                file_paths=["CFB.pdf", "simulado-BNB.pdf"]
            )],
            embedder={
                "provider": "huggingface",
                "config": {
                    "model": "all-MiniLM-L6-v2",
                },
            },
        )