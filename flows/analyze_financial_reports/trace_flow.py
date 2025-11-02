#!/usr/bin/env python
"""
Add instrumentation/logging to the flow to see what's happening at each step.
This creates a traced version of your flow with detailed logging.

Usage:
    python trace_flow.py --company "Apple Inc." --persona value_investing
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


class FlowTracer:
    """Add detailed logging to track flow execution."""
    
    def __init__(self, log_file: str = None):
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"flow_trace_{timestamp}.log"
        
        self.log_file = Path(log_file)
        self.log_entries = []
        
        print(f"📝 Logging to: {self.log_file}")
    
    def log(self, stage: str, event: str, data: any = None):
        """Log an event with optional data."""
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "stage": stage,
            "event": event,
        }
        
        if data is not None:
            # Convert to JSON-serializable format
            try:
                if hasattr(data, 'model_dump'):
                    entry["data"] = data.model_dump()
                elif hasattr(data, '__dict__'):
                    entry["data"] = str(data)
                else:
                    entry["data"] = data
            except:
                entry["data"] = str(data)
        
        self.log_entries.append(entry)
        
        # Also print to console
        print(f"\n[{timestamp}] {stage} - {event}")
        if data is not None and isinstance(data, (dict, list)):
            print(f"  Data preview: {str(data)[:100]}...")
    
    def save(self):
        """Save log entries to file."""
        with open(self.log_file, 'w') as f:
            json.dump(self.log_entries, f, indent=2, default=str)
        
        print(f"\n💾 Log saved to: {self.log_file}")
    
    def print_summary(self):
        """Print a summary of the execution."""
        print("\n" + "=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)
        
        stages = {}
        for entry in self.log_entries:
            stage = entry["stage"]
            if stage not in stages:
                stages[stage] = []
            stages[stage].append(entry["event"])
        
        for stage, events in stages.items():
            print(f"\n{stage}:")
            for event in events:
                print(f"  • {event}")


def run_traced_flow(company: str, persona_name: str):
    """Run the flow with detailed tracing."""
    from analyze_financial_reports.main import (
        FinancialReportFlow,
        ReportState,
        load_persona_from_yaml,
        get_default_persona,
    )
    
    tracer = FlowTracer()
    
    try:
        # Load persona
        tracer.log("SETUP", "Loading investment persona")
        if persona_name:
            persona = load_persona_from_yaml(persona_name)
        else:
            persona = get_default_persona()
        
        tracer.log("SETUP", f"Persona loaded: {persona.name}", persona)
        
        # Create initial state
        tracer.log("SETUP", "Creating initial state")
        state = ReportState(
            company_name=company,
            investment_persona=persona,
        )
        
        tracer.log("SETUP", "Initial state created", {
            "company": company,
            "persona": persona.name,
            "strategy": persona.strategy_type,
        })
        
        # Create flow
        tracer.log("FLOW", "Creating flow instance")
        flow = FinancialReportFlow()
        
        # Patch flow methods to add logging
        original_generate_questions = flow.generate_questions
        original_create_outline = flow.create_outline
        original_research_sections = flow.research_sections
        original_write_sections = flow.write_sections
        
        def traced_generate_questions():
            tracer.log("STAGE_1", "Starting question generation")
            result = original_generate_questions()
            tracer.log("STAGE_1", "Question generation completed", {
                "num_questions": len(result) if result else 0,
                "questions": result,
            })
            return result
        
        def traced_create_outline():
            tracer.log("STAGE_2", "Starting outline creation")
            tracer.log("STAGE_2", "Input questions", {
                "num_questions": len(flow.state.research_questions),
            })
            result = original_create_outline()
            tracer.log("STAGE_2", "Outline creation completed", {
                "num_sections": len(result) if result else 0,
                "sections": result,
            })
            return result
        
        async def traced_research_sections():
            tracer.log("STAGE_3", "Starting parallel research")
            tracer.log("STAGE_3", "Sections to research", {
                "num_sections": len(flow.state.report_outline),
            })
            result = await original_research_sections()
            tracer.log("STAGE_3", "Research completed", {
                "num_results": len(result) if result else 0,
            })
            return result
        
        async def traced_write_sections():
            tracer.log("STAGE_4", "Starting parallel writing")
            tracer.log("STAGE_4", "Sections to write", {
                "num_sections": len(flow.state.report_outline),
            })
            result = await original_write_sections()
            tracer.log("STAGE_4", "Writing completed", {
                "num_sections": len(result) if result else 0,
            })
            return result
        
        # Apply patches
        flow.generate_questions = traced_generate_questions
        flow.create_outline = traced_create_outline
        flow.research_sections = traced_research_sections
        flow.write_sections = traced_write_sections
        
        # Run the flow
        tracer.log("FLOW", "Starting flow execution")
        flow.kickoff(inputs=state.dict())
        tracer.log("FLOW", "Flow execution completed")
        
    except Exception as e:
        tracer.log("ERROR", f"Flow failed: {type(e).__name__}", {
            "error": str(e),
        })
        import traceback
        print("\n" + "=" * 80)
        print("ERROR DETAILS")
        print("=" * 80)
        traceback.print_exc()
    
    finally:
        # Save log and print summary
        tracer.save()
        tracer.print_summary()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run flow with detailed execution tracing"
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
    
    args = parser.parse_args()
    
    print("\n🔍 FLOW TRACER")
    print("=" * 80)
    print(f"Company: {args.company}")
    print(f"Persona: {args.persona or 'default (Value Investing)'}")
    print("=" * 80 + "\n")
    
    run_traced_flow(args.company, args.persona)
