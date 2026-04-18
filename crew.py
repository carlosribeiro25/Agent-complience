import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource

load_dotenv(override=True)

pdf_tool = PDFKnowledgeSource(
    file_paths=["CFB.pdf"]
)

@CrewBase
class ComplienceCrew:
    tasks_config = "config/tasks.yaml"
    agents_config = "config/agents.yaml"

    @agent
    def especialista_estudos(self) -> Agent:
        llm = LLM(model="gpt-5")
        return Agent(
            config=self.agents_config["especialista_estudos"],
            verbose=True,
            tools=[],
            llm=llm,
        )
    
    @task
    def responder_perguntas_especialista_estudos(self) -> Task:
        return Task(
            config=self.tasks_config["responder_perguntas_especialista_estudos"],
            agent=self.especialista_estudos()
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.especialista_estudos()],
            tasks=[
                self.responder_perguntas_especialista_estudos(),
            ],
            process=Process.sequential,
            verbose=True,
            knowledge_sources=[pdf_tool],
            embedder={
                "provider": "huggingface",
                "config": {
                    "model": "all-MiniLM-L6-v2",
                },
            },
        )