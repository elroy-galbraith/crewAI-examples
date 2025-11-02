from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from analyze_financial_reports.models import QuestionsList


@CrewBase
class QuestionGenerationCrew:
    """Question Generation Crew - Simulates PM and Analyst conversation"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = LLM(model="gpt-4o")

    @agent
    def portfolio_manager(self) -> Agent:
        """Portfolio Manager agent who asks strategic questions"""
        search_tool = SerperDevTool()
        return Agent(
            config=self.agents_config["portfolio_manager"],
            tools=[search_tool],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def analyst(self) -> Agent:
        """Financial Analyst who helps formulate research questions"""
        search_tool = SerperDevTool()
        return Agent(
            config=self.agents_config["analyst"],
            tools=[search_tool],
            llm=self.llm,
            verbose=True,
        )

    @task
    def simulate_conversation(self) -> Task:
        """Simulate the conversation between PM and analyst"""
        return Task(
            config=self.tasks_config["simulate_conversation"],
        )

    @task
    def extract_questions(self) -> Task:
        """Extract structured questions from the conversation"""
        return Task(
            config=self.tasks_config["extract_questions"],
            output_pydantic=QuestionsList,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Question Generation Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
