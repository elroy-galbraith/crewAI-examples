from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from analyze_financial_reports.models import CompletedSection


@CrewBase
class ReportWriterCrew:
    """Report Writer Crew - Writes individual report sections"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = LLM(model="gpt-4o")

    @agent
    def report_writer(self) -> Agent:
        """Report writer who creates polished sections"""
        return Agent(
            config=self.agents_config["report_writer"],
            llm=self.llm,
            verbose=True,
        )

    @task
    def write_section(self) -> Task:
        """Write the report section"""
        return Task(
            config=self.tasks_config["write_section"],
            output_pydantic=CompletedSection,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Report Writer Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
