from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from analyze_financial_reports.tools.financial_tools import (
    FinancialReportRAGTool,
    RatioCalculatorTool,
    VisualizationTool,
)
from analyze_financial_reports.models import FinancialData


@CrewBase
class ResearchSectionCrew:
    """Research Section Crew - Researches and analyzes one section"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = LLM(model="gpt-4o")

    @agent
    def financial_researcher(self) -> Agent:
        """Financial researcher who gathers data"""
        # Initialize tools based on what's needed
        tools = []
        tools.append(FinancialReportRAGTool())
        tools.append(SerperDevTool())
        
        return Agent(
            config=self.agents_config["financial_researcher"],
            tools=tools,
            llm=self.llm,
            verbose=True,
        )

    @agent
    def data_analyst(self) -> Agent:
        """Data analyst who performs calculations and creates visualizations"""
        tools = []
        tools.append(RatioCalculatorTool())
        tools.append(VisualizationTool())
        
        return Agent(
            config=self.agents_config["data_analyst"],
            tools=tools,
            llm=self.llm,
            verbose=True,
        )

    @task
    def gather_research(self) -> Task:
        """Gather research data for the section"""
        return Task(
            config=self.tasks_config["gather_research"],
        )

    @task
    def analyze_and_visualize(self) -> Task:
        """Analyze data and create visualizations"""
        return Task(
            config=self.tasks_config["analyze_and_visualize"],
            output_pydantic=FinancialData,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Section Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
