#!/usr/bin/env python
"""
Debug script for testing CrewAI flow components step by step.

This script allows you to:
1. Test individual crews outside the flow
2. Validate output formats
3. Test function calling/tool usage
4. Run specific stages without running the entire flow
5. Inspect intermediate outputs

Usage:
    # Test question generation crew
    python debug_flow.py --step questions --company "Apple Inc."
    
    # Test outline crew
    python debug_flow.py --step outline --company "Apple Inc."
    
    # Test research crew
    python debug_flow.py --step research --company "Apple Inc."
    
    # Test all steps sequentially with debugging
    python debug_flow.py --step all --company "Apple Inc." --verbose
    
    # Test a specific crew with custom inputs
    python debug_flow.py --step questions --company "Microsoft" --persona growth_investing
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

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
    ReportSection,
    InvestmentPersona,
)
from analyze_financial_reports.main import load_persona_from_yaml, get_default_persona


class FlowDebugger:
    """Debug helper for testing flow components."""
    
    def __init__(self, company_name: str, persona: InvestmentPersona, verbose: bool = False):
        self.company_name = company_name
        self.persona = persona
        self.verbose = verbose
        self.results = {}
    
    def print_separator(self, title: str):
        """Print a visual separator."""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def print_json(self, label: str, data: Any):
        """Pretty print JSON data."""
        print(f"\n{label}:")
        print(json.dumps(data, indent=2, default=str))
    
    def validate_output_format(self, output: Any, expected_keys: List[str], stage: str):
        """Validate that the output has expected structure."""
        print(f"\n🔍 Validating {stage} output format...")
        
        if not isinstance(output, dict):
            print(f"❌ ERROR: Output is not a dictionary. Type: {type(output)}")
            print(f"Output: {output}")
            return False
        
        missing_keys = [key for key in expected_keys if key not in output]
        if missing_keys:
            print(f"❌ ERROR: Missing keys: {missing_keys}")
            print(f"Available keys: {list(output.keys())}")
            return False
        
        print(f"✅ Output format is valid")
        print(f"   Keys found: {list(output.keys())}")
        return True
    
    def test_question_generation(self) -> Dict[str, Any]:
        """Test Step 1: Question Generation Crew."""
        self.print_separator("STEP 1: Testing Question Generation Crew")
        
        print(f"Company: {self.company_name}")
        print(f"Strategy: {self.persona.strategy_type}")
        
        inputs = {
            "company_name": self.company_name,
            "investment_strategy": self.persona.strategy_type,
            "investment_persona": self.persona.model_dump_json(indent=2),
        }
        
        if self.verbose:
            self.print_json("Input to crew", inputs)
        
        print("\n🚀 Running Question Generation Crew...")
        
        try:
            crew = QuestionGenerationCrew()
            output = crew.crew().kickoff(inputs=inputs)
            
            print("\n✅ Crew completed successfully")
            print(f"Output type: {type(output)}")
            
            # Validate output format
            if self.validate_output_format(output, ["questions"], "Question Generation"):
                questions = output["questions"]
                print(f"\n📋 Generated {len(questions)} questions:")
                for i, q in enumerate(questions, 1):
                    if isinstance(q, ResearchQuestion):
                        print(f"  {i}. [{q.category}] {q.question}")
                        print(f"     Priority: {q.priority}")
                    else:
                        print(f"  {i}. {q}")
                
                self.results['questions'] = questions
                
                if self.verbose:
                    self.print_json("Full output", output)
            
            return output
            
        except Exception as e:
            print(f"\n❌ ERROR in Question Generation:")
            print(f"   {type(e).__name__}: {str(e)}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            raise
    
    def test_outline_generation(self, questions: List[ResearchQuestion] = None) -> Dict[str, Any]:
        """Test Step 2: Report Outline Crew."""
        self.print_separator("STEP 2: Testing Report Outline Crew")
        
        if questions is None:
            print("⚠️  No questions provided. Using sample questions.")
            questions = [
                ResearchQuestion(
                    question=f"What is {self.company_name}'s current P/E ratio?",
                    category="Financial Ratios",
                    priority="high"
                ),
                ResearchQuestion(
                    question=f"How has {self.company_name}'s revenue grown?",
                    category="Growth Metrics",
                    priority="high"
                ),
            ]
        
        print(f"Company: {self.company_name}")
        print(f"Questions to process: {len(questions)}")
        
        # Convert questions to JSON
        questions_json = [q.model_dump_json() for q in questions]
        
        inputs = {
            "company_name": self.company_name,
            "investment_strategy": self.persona.strategy_type,
            "research_questions": json.dumps(questions_json, indent=2),
            "investment_persona": self.persona.model_dump_json(indent=2),
        }
        
        if self.verbose:
            self.print_json("Input to crew", inputs)
        
        print("\n🚀 Running Report Outline Crew...")
        
        try:
            crew = ReportOutlineCrew()
            output = crew.crew().kickoff(inputs=inputs)
            
            print("\n✅ Crew completed successfully")
            print(f"Output type: {type(output)}")
            
            # Validate output format
            if self.validate_output_format(output, ["sections"], "Report Outline"):
                sections = output["sections"]
                print(f"\n📋 Generated {len(sections)} sections:")
                for section in sections:
                    if isinstance(section, ReportSection):
                        print(f"  {section.order}. {section.title}")
                        print(f"     Tools: {', '.join(section.required_tools)}")
                        print(f"     Description: {section.description[:80]}...")
                    else:
                        print(f"  {section}")
                
                self.results['sections'] = sections
                
                if self.verbose:
                    self.print_json("Full output", output)
            
            return output
            
        except Exception as e:
            print(f"\n❌ ERROR in Outline Generation:")
            print(f"   {type(e).__name__}: {str(e)}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            raise
    
    def test_research_section(self, section: ReportSection = None) -> Dict[str, Any]:
        """Test Step 3: Research Section Crew."""
        self.print_separator("STEP 3: Testing Research Section Crew")
        
        if section is None:
            print("⚠️  No section provided. Using sample section.")
            section = ReportSection(
                title="Financial Overview",
                description=f"Analyze {self.company_name}'s key financial metrics",
                required_tools=["financial_rag", "ratio_calculator"],
                order=1
            )
        
        print(f"Company: {self.company_name}")
        print(f"Section: {section.title}")
        print(f"Required tools: {', '.join(section.required_tools)}")
        
        inputs = {
            "company_name": self.company_name,
            "section_title": section.title,
            "section_description": section.description,
            "required_tools": ", ".join(section.required_tools),
            "investment_persona": self.persona.model_dump_json(indent=2),
        }
        
        if self.verbose:
            self.print_json("Input to crew", inputs)
        
        print("\n🚀 Running Research Section Crew...")
        
        try:
            crew = ResearchSectionCrew()
            output = crew.crew().kickoff(inputs=inputs)
            
            print("\n✅ Crew completed successfully")
            print(f"Output type: {type(output)}")
            
            # Validate output format (more lenient for research)
            expected_keys = ["section_title"]
            if self.validate_output_format(output, expected_keys, "Research Section"):
                print(f"\n📊 Research Results:")
                print(f"   Section: {output.get('section_title', 'N/A')}")
                print(f"   Metrics: {len(str(output.get('metrics', {})))} chars")
                print(f"   Calculations: {len(str(output.get('calculations', {})))} chars")
                print(f"   Notes: {len(output.get('research_notes', ''))} chars")
                
                if self.verbose:
                    self.print_json("Full output", output)
            
            return output
            
        except Exception as e:
            print(f"\n❌ ERROR in Research Section:")
            print(f"   {type(e).__name__}: {str(e)}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            raise
    
    def test_tools_directly(self):
        """Test tools directly outside of the crew."""
        self.print_separator("TESTING TOOLS DIRECTLY")
        
        from analyze_financial_reports.tools.financial_tools import (
            FinancialReportRAGTool,
            RatioCalculatorTool,
        )
        
        # Test RAG tool
        print("\n1. Testing Financial Report RAG Tool...")
        try:
            rag_tool = FinancialReportRAGTool()
            result = rag_tool._run(
                company_name=self.company_name,
                query="What was the revenue for the latest quarter?"
            )
            print(f"✅ RAG Tool Result ({len(result)} chars):")
            print(result[:200] + "..." if len(result) > 200 else result)
        except Exception as e:
            print(f"❌ RAG Tool Error: {e}")
        
        # Test Ratio Calculator
        print("\n2. Testing Ratio Calculator Tool...")
        try:
            calc_tool = RatioCalculatorTool()
            result = calc_tool._run(
                financial_data={"price": 150.0, "eps": 6.0},
                ratio_type="PE"
            )
            print(f"✅ Calculator Result:")
            self.print_json("Calculation", result)
        except Exception as e:
            print(f"❌ Calculator Error: {e}")
    
    def run_all_steps(self):
        """Run all steps sequentially for complete debugging."""
        self.print_separator("RUNNING ALL STEPS SEQUENTIALLY")
        
        try:
            # Step 1: Questions
            questions_output = self.test_question_generation()
            questions = questions_output.get("questions", [])
            
            # Step 2: Outline
            outline_output = self.test_outline_generation(questions)
            sections = outline_output.get("sections", [])
            
            # Step 3: Research (just test first section)
            if sections:
                self.test_research_section(sections[0])
            
            self.print_separator("ALL STEPS COMPLETED")
            print("\n✅ All steps completed successfully!")
            print(f"\nResults summary:")
            print(f"  - Questions generated: {len(questions)}")
            print(f"  - Sections created: {len(sections)}")
            
        except Exception as e:
            print(f"\n❌ Flow stopped due to error: {e}")
            return False
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Debug CrewAI Flow Components Step by Step",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        '--step',
        choices=['questions', 'outline', 'research', 'tools', 'all'],
        default='all',
        help='Which step to test'
    )
    
    parser.add_argument(
        '--company', '-c',
        default='Apple Inc.',
        help='Company name to analyze'
    )
    
    parser.add_argument(
        '--persona', '-p',
        default=None,
        help='Investment persona (e.g., growth_investing, value_investing)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output including full JSON'
    )
    
    args = parser.parse_args()
    
    # Load persona
    if args.persona:
        try:
            persona = load_persona_from_yaml(args.persona)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return
    else:
        persona = get_default_persona()
    
    # Create debugger
    debugger = FlowDebugger(args.company, persona, args.verbose)
    
    # Run selected step
    try:
        if args.step == 'questions':
            debugger.test_question_generation()
        elif args.step == 'outline':
            debugger.test_outline_generation()
        elif args.step == 'research':
            debugger.test_research_section()
        elif args.step == 'tools':
            debugger.test_tools_directly()
        elif args.step == 'all':
            debugger.run_all_steps()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
