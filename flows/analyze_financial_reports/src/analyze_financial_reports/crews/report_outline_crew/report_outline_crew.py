from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from analyze_financial_reports.models import ReportOutline


@CrewBase
class ReportOutlineCrew:
    """Report Outline Crew - Creates structured report outline"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = LLM(model="gpt-4o")

    @agent
    def research_planner(self) -> Agent:
        """Research planner who organizes the analysis"""
        return Agent(
            config=self.agents_config["research_planner"],
            llm=self.llm,
            verbose=True,
        )

    @task
    def create_outline(self) -> Task:
        """Create the report outline"""
        return Task(
            config=self.tasks_config["create_outline"],
            output_pydantic=ReportOutline,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Report Outline Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
