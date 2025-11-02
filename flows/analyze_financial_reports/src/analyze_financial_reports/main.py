#!/usr/bin/env python
import asyncio
import os
import sys
import uuid
import yaml
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel, Field

from analyze_financial_reports.crews.question_generation_crew.question_generation_crew import (
    QuestionGenerationCrew,
)
from analyze_financial_reports.crews.report_outline_crew.report_outline_crew import (
    ReportOutlineCrew,
)
from analyze_financial_reports.crews.research_section_crew.research_section_crew import (
    ResearchSectionCrew,
)
from analyze_financial_reports.crews.report_writer_crew.report_writer_crew import (
    ReportWriterCrew,
)
from analyze_financial_reports.models import (
    ResearchQuestion,
    ReportOutline,
    ReportSection,
    FinancialData,
    CompletedSection,
    CompanyScore,
    InvestmentPersona,
)


def load_persona_from_yaml(persona_name: str) -> InvestmentPersona:
    """
    Load an investment persona from a YAML file.
    
    Args:
        persona_name: Name of the persona file (with or without .yaml extension)
                     e.g., "value_investing" or "value_investing.yaml"
    
    Returns:
        InvestmentPersona object
    """
    if not persona_name.endswith('.yaml'):
        persona_name = f"{persona_name}.yaml"
    
    # Get the path to the personas directory
    current_file = Path(__file__)
    personas_dir = current_file.parent / "config" / "investment_personas"
    persona_path = personas_dir / persona_name
    
    if not persona_path.exists():
        raise FileNotFoundError(
            f"Persona file not found: {persona_path}\n"
            f"Available personas: {', '.join([f.stem for f in personas_dir.glob('*.yaml')])}"
        )
    
    with open(persona_path, 'r') as f:
        persona_data = yaml.safe_load(f)
    
    # Convert criteria dict to JSON string
    if 'criteria' in persona_data and isinstance(persona_data['criteria'], dict):
        persona_data['criteria'] = json.dumps(persona_data['criteria'])
    
    return InvestmentPersona(**persona_data)


def get_default_persona() -> InvestmentPersona:
    """Get the default Value Investing persona."""
    return InvestmentPersona(
        name="Value Investing Strategy",
        strategy_type="Value",
        key_metrics=["P/E Ratio", "P/B Ratio", "Dividend Yield", "ROE", "Debt-to-Equity"],
        criteria=json.dumps({
            "max_pe": 15,
            "max_pb": 1.5,
            "min_dividend_yield": 2.0,
            "min_roe": 15,
            "max_debt_to_equity": 0.5,
        }),
        risk_tolerance="low",
        time_horizon="long-term",
    )


class ReportState(BaseModel):
    """State management for the financial report flow."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str = "Apple Inc."
    investment_persona: InvestmentPersona = Field(default_factory=get_default_persona)
    research_questions: List[ResearchQuestion] = []
    report_outline: List[ReportSection] = []
    research_data: List[FinancialData] = []
    report_sections: List[CompletedSection] = []
    final_score: Optional[CompanyScore] = None


class FinancialReportFlow(Flow[ReportState]):
    """
    Financial Report Generation Flow
    
    This flow orchestrates multiple crews to:
    1. Generate research questions through PM-Analyst conversation
    2. Create a structured report outline
    3. Research each section in parallel
    4. Write each section in parallel
    5. Compile and score the final report
    """
    
    initial_state = ReportState

    @start()
    def generate_questions(self):
        """
        Stage 1: Generate research questions through simulated conversation
        between portfolio manager and analyst.
        """
        print("=" * 80)
        print("STAGE 1: Generating Research Questions")
        print("=" * 80)
        
        output = (
            QuestionGenerationCrew()
            .crew()
            .kickoff(
                inputs={
                    "company_name": self.state.company_name,
                    "investment_strategy": self.state.investment_persona.strategy_type,
                    "investment_persona": self.state.investment_persona.model_dump_json(indent=2),
                }
            )
        )

        questions = output["questions"]
        print(f"\nGenerated {len(questions)} research questions")
        
        self.state.research_questions = questions
        return questions

    @listen(generate_questions)
    def create_outline(self):
        """
        Stage 2: Create report outline based on research questions.
        """
        print("\n" + "=" * 80)
        print("STAGE 2: Creating Report Outline")
        print("=" * 80)
        
        # Convert questions to JSON for the crew
        questions_json = [q.model_dump_json() for q in self.state.research_questions]
        
        output = (
            ReportOutlineCrew()
            .crew()
            .kickoff(
                inputs={
                    "company_name": self.state.company_name,
                    "investment_strategy": self.state.investment_persona.strategy_type,
                    "research_questions": json.dumps(questions_json, indent=2),
                    "investment_persona": self.state.investment_persona.model_dump_json(indent=2),
                }
            )
        )

        sections = output["sections"]
        print(f"\nCreated outline with {len(sections)} sections")
        for section in sections:
            print(f"  {section.order}. {section.title}")
        
        self.state.report_outline = sections
        return sections

    @listen(create_outline)
    async def research_sections(self):
        """
        Stage 3: Research all sections in parallel.
        """
        print("\n" + "=" * 80)
        print("STAGE 3: Researching All Sections (Parallel)")
        print("=" * 80)
        
        async def research_single_section(section: ReportSection):
            print(f"\nResearching: {section.title}")
            
            output = (
                ResearchSectionCrew()
                .crew()
                .kickoff(
                    inputs={
                        "company_name": self.state.company_name,
                        "section_title": section.title,
                        "section_description": section.description,
                        "required_tools": ", ".join(section.required_tools),
                        "investment_persona": self.state.investment_persona.model_dump_json(indent=2),
                    }
                )
            )
            
            # Extract the FinancialData from output.pydantic
            # The crew returns a CrewOutput object with a pydantic attribute
            # that contains the structured output (FinancialData model)
            financial_data = output.pydantic
            
            return financial_data

        # Create tasks for all sections
        tasks = []
        for section in self.state.report_outline:
            task = asyncio.create_task(research_single_section(section))
            tasks.append(task)

        # Execute all research in parallel
        research_results = await asyncio.gather(*tasks)
        self.state.research_data = research_results
        
        print(f"\nCompleted research for {len(research_results)} sections")
        return research_results

    @listen(research_sections)
    async def write_sections(self):
        """
        Stage 4: Write all report sections in parallel.
        """
        print("\n" + "=" * 80)
        print("STAGE 4: Writing All Sections (Parallel)")
        print("=" * 80)
        
        async def write_single_section(section: ReportSection, research_data: FinancialData):
            print(f"\nWriting: {section.title}")
            
            # Find matching research data
            outline_json = [s.model_dump_json() for s in self.state.report_outline]
            
            output = (
                ReportWriterCrew()
                .crew()
                .kickoff(
                    inputs={
                        "company_name": self.state.company_name,
                        "investment_strategy": self.state.investment_persona.strategy_type,
                        "section_title": section.title,
                        "section_description": section.description,
                        "section_order": section.order,
                        "research_data": research_data.model_dump_json(indent=2),
                        "report_outline": json.dumps(outline_json, indent=2),
                        "investment_persona": self.state.investment_persona.model_dump_json(indent=2),
                    }
                )
            )
            
            # Extract the CompletedSection from output.pydantic
            # The crew returns a CrewOutput object with a pydantic attribute
            # that contains the structured output (CompletedSection model)
            completed_section = output.pydantic
            
            return completed_section

        # Create tasks for all sections
        tasks = []
        for section, research_data in zip(self.state.report_outline, self.state.research_data):
            task = asyncio.create_task(write_single_section(section, research_data))
            tasks.append(task)

        # Execute all writing in parallel
        written_sections = await asyncio.gather(*tasks)
        
        # Sort by order
        written_sections.sort(key=lambda x: x.order)
        self.state.report_sections = written_sections
        
        print(f"\nCompleted writing {len(written_sections)} sections")
        return written_sections

    @listen(write_sections)
    async def compile_and_score_report(self):
        """
        Stage 5: Compile all sections, deduplicate content, and score the company.
        """
        print("\n" + "=" * 80)
        print("STAGE 5: Compiling Report and Scoring Company")
        print("=" * 80)
        
        # Compile the report
        report_content = f"# Financial Analysis Report: {self.state.company_name}\n\n"
        report_content += f"**Investment Strategy:** {self.state.investment_persona.name}\n\n"
        report_content += "---\n\n"
        
        for section in self.state.report_sections:
            report_content += f"## {section.title}\n\n"
            report_content += f"{section.content}\n\n"
            report_content += "---\n\n"
        
        # TODO: Implement LLM-based deduplication
        # This would use an LLM to identify and remove duplicate content
        
        # Calculate score based on investment criteria
        score = self._calculate_company_score()
        self.state.final_score = score
        
        # Add score to report
        report_content += "## Investment Score\n\n"
        report_content += f"**Overall Score:** {score.overall_score}/100\n\n"
        report_content += f"**Recommendation:** {score.recommendation}\n\n"
        report_content += f"**Meets Investment Criteria:** {'Yes' if score.meets_criteria else 'No'}\n\n"
        
        if score.key_strengths:
            report_content += "### Key Strengths\n\n"
            for strength in score.key_strengths:
                report_content += f"- {strength}\n"
            report_content += "\n"
        
        if score.key_concerns:
            report_content += "### Key Concerns\n\n"
            for concern in score.key_concerns:
                report_content += f"- {concern}\n"
            report_content += "\n"
        
        if score.summary:
            report_content += f"### Summary\n\n{score.summary}\n\n"
        
        # Save the report
        filename = f"./{self.state.company_name.replace(' ', '_')}_Financial_Report.md"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(report_content)
        
        print(f"\n✅ Report saved as: {filename}")
        print(f"📊 Overall Score: {score.overall_score}/100")
        print(f"💡 Recommendation: {score.recommendation}")
        
        return report_content

    def _calculate_company_score(self) -> CompanyScore:
        """
        Calculate a score for the company based on research data and investment criteria.
        
        This is a simplified implementation. In production, this would use an LLM
        to analyze all research data against the investment criteria.
        """
        # Placeholder scoring logic
        # In production, this would analyze all research_data against investment_persona.criteria
        
        category_scores = {
            "Financial Health": 75.0,
            "Growth Prospects": 80.0,
            "Valuation": 70.0,
            "Competitive Position": 85.0,
            "Risk Profile": 65.0,
        }
        
        overall_score = sum(category_scores.values()) / len(category_scores)
        
        # Determine recommendation
        if overall_score >= 80:
            recommendation = "Strong Buy"
        elif overall_score >= 70:
            recommendation = "Buy"
        elif overall_score >= 60:
            recommendation = "Hold"
        elif overall_score >= 50:
            recommendation = "Sell"
        else:
            recommendation = "Strong Sell"
        
        meets_criteria = overall_score >= 70
        
        return CompanyScore(
            company_name=self.state.company_name,
            overall_score=round(overall_score, 2),
            category_scores=json.dumps(category_scores),
            meets_criteria=meets_criteria,
            recommendation=recommendation,
            key_strengths=[
                "Strong competitive position in the market",
                "Consistent revenue growth",
                "Solid balance sheet",
            ],
            key_concerns=[
                "Valuation appears slightly elevated",
                "Industry faces regulatory headwinds",
            ],
            summary=f"Based on the {self.state.investment_persona.strategy_type} investment strategy, "
                    f"{self.state.company_name} scores {overall_score:.1f}/100. "
                    f"The analysis suggests a {recommendation} recommendation.",
        )


def kickoff(company: Optional[str] = None, persona: Optional[str] = None):
    """
    Run the financial report flow.
    
    Args:
        company: Company name to analyze (e.g., "Microsoft Corporation")
                If None, uses default "Apple Inc."
        persona: Investment persona to use. Can be:
                - A persona name (e.g., "growth_investing", "value_investing")
                - Path to a custom YAML file
                - If None, uses default Value Investing strategy
    
    Examples:
        # Use defaults (Apple Inc., Value Investing)
        kickoff()
        
        # Analyze Microsoft with default strategy
        kickoff(company="Microsoft Corporation")
        
        # Analyze Apple with Growth strategy
        kickoff(persona="growth_investing")
        
        # Analyze Tesla with Growth strategy
        kickoff(company="Tesla Inc.", persona="growth_investing")
        
        # Use custom persona file
        kickoff(company="NVIDIA", persona="path/to/custom_persona.yaml")
    """
    # Create flow with custom state if parameters provided
    if company or persona:
        state_kwargs = {}
        
        if company:
            state_kwargs['company_name'] = company
        
        if persona:
            try:
                state_kwargs['investment_persona'] = load_persona_from_yaml(persona)
            except FileNotFoundError as e:
                print(f"Error: {e}")
                return
        
        # Create custom initial state and pass it to kickoff
        initial_state = ReportState(**state_kwargs)
        flow = FinancialReportFlow()
        flow.kickoff(inputs=initial_state.dict())
    else:
        flow = FinancialReportFlow()
        flow.kickoff()


def plot():
    """Visualize the flow structure."""
    flow = FinancialReportFlow()
    flow.plot()


if __name__ == "__main__":
    # Parse command-line arguments for easy usage
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate financial analysis reports using AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use defaults (Apple Inc., Value Investing)
  python main.py
  
  # Analyze a different company
  python main.py --company "Microsoft Corporation"
  
  # Use a different investment strategy
  python main.py --persona growth_investing
  
  # Analyze specific company with specific strategy
  python main.py --company "Tesla Inc." --persona growth_investing
  
  # List available personas
  python main.py --list-personas
  
  # Visualize the flow
  python main.py --plot

Available Personas:
  - value_investing (default)
  - growth_investing
  - dividend_investing
  - garp_investing
        """
    )
    
    parser.add_argument(
        '--company', '-c',
        type=str,
        help='Company name to analyze (e.g., "Microsoft Corporation")'
    )
    
    parser.add_argument(
        '--persona', '-p',
        type=str,
        help='Investment persona to use (e.g., growth_investing, value_investing)'
    )
    
    parser.add_argument(
        '--list-personas',
        action='store_true',
        help='List all available investment personas'
    )
    
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Visualize the flow structure instead of running it'
    )
    
    args = parser.parse_args()
    
    if args.list_personas:
        # List available personas
        current_file = Path(__file__)
        personas_dir = current_file.parent / "config" / "investment_personas"
        print("\n📊 Available Investment Personas:\n")
        for yaml_file in sorted(personas_dir.glob('*.yaml')):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                print(f"  • {yaml_file.stem}")
                print(f"    Name: {data.get('name', 'N/A')}")
                print(f"    Type: {data.get('strategy_type', 'N/A')}")
                print(f"    Risk: {data.get('risk_tolerance', 'N/A')}")
                print()
    elif args.plot:
        plot()
    else:
        kickoff(company=args.company, persona=args.persona)
