#!/usr/bin/env python
"""
Inspect crew configurations to debug output format issues.
This helps identify mismatches between task configs and expected outputs.
"""

import sys
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def inspect_crew_config(crew_name: str):
    """Inspect a crew's configuration files."""
    print("=" * 80)
    print(f"INSPECTING {crew_name.upper()} CREW")
    print("=" * 80)
    
    crew_dir = Path(__file__).parent / "src" / "analyze_financial_reports" / "crews" / crew_name
    
    if not crew_dir.exists():
        print(f"❌ Crew directory not found: {crew_dir}")
        return
    
    # Check agents.yaml
    agents_file = crew_dir / "config" / "agents.yaml"
    if agents_file.exists():
        print(f"\n📋 AGENTS ({agents_file}):")
        print("-" * 80)
        with open(agents_file) as f:
            agents = yaml.safe_load(f)
            for agent_name, agent_config in agents.items():
                print(f"\n  Agent: {agent_name}")
                print(f"    Role: {agent_config.get('role', 'N/A')}")
                print(f"    Goal: {agent_config.get('goal', 'N/A')[:60]}...")
                if 'tools' in agent_config:
                    print(f"    Tools: {agent_config.get('tools', [])}")
    
    # Check tasks.yaml
    tasks_file = crew_dir / "config" / "tasks.yaml"
    if tasks_file.exists():
        print(f"\n📋 TASKS ({tasks_file}):")
        print("-" * 80)
        with open(tasks_file) as f:
            tasks = yaml.safe_load(f)
            for task_name, task_config in tasks.items():
                print(f"\n  Task: {task_name}")
                print(f"    Description: {task_config.get('description', 'N/A')[:60]}...")
                print(f"    Expected Output: {task_config.get('expected_output', 'N/A')[:60]}...")
                print(f"    Agent: {task_config.get('agent', 'N/A')}")
                
                # Key: Check output configuration
                if 'output_pydantic' in task_config:
                    print(f"    ✅ Output Pydantic: {task_config['output_pydantic']}")
                elif 'output_json' in task_config:
                    print(f"    ✅ Output JSON: {task_config['output_json']}")
                else:
                    print(f"    ⚠️  No structured output defined (will be raw text)")
    
    # Check the crew Python file
    crew_file = crew_dir / f"{crew_name}.py"
    if crew_file.exists():
        print(f"\n📋 CREW CODE ({crew_file}):")
        print("-" * 80)
        
        with open(crew_file) as f:
            content = f.read()
            
            # Look for output_pydantic definitions
            if 'output_pydantic' in content:
                print("    ✅ Found output_pydantic in code")
                # Extract the lines
                for i, line in enumerate(content.split('\n')):
                    if 'output_pydantic' in line:
                        print(f"       Line {i+1}: {line.strip()}")
            else:
                print("    ⚠️  No output_pydantic found in code")
            
            # Look for output_json definitions
            if 'output_json' in content:
                print("    ✅ Found output_json in code")
                for i, line in enumerate(content.split('\n')):
                    if 'output_json' in line:
                        print(f"       Line {i+1}: {line.strip()}")


def inspect_models():
    """Inspect the models.py file to see expected output structures."""
    print("\n" + "=" * 80)
    print("INSPECTING PYDANTIC MODELS")
    print("=" * 80)
    
    from analyze_financial_reports.models import (
        ResearchQuestion,
        QuestionsList,
        ReportSection,
        ReportOutline,
        FinancialData,
        CompletedSection,
        CompanyScore,
    )
    
    models = [
        ("ResearchQuestion", ResearchQuestion),
        ("QuestionsList", QuestionsList),
        ("ReportSection", ReportSection),
        ("ReportOutline", ReportOutline),
        ("FinancialData", FinancialData),
        ("CompletedSection", CompletedSection),
        ("CompanyScore", CompanyScore),
    ]
    
    for model_name, model_class in models:
        print(f"\n📦 {model_name}")
        print("-" * 80)
        schema = model_class.model_json_schema()
        
        if 'properties' in schema:
            for field_name, field_info in schema['properties'].items():
                field_type = field_info.get('type', 'unknown')
                required = field_name in schema.get('required', [])
                default = field_info.get('default', None)
                
                print(f"  • {field_name}: {field_type}", end="")
                if required:
                    print(" (required)", end="")
                if default is not None:
                    print(f" [default: {default}]", end="")
                print()


def compare_task_to_model(crew_name: str, task_name: str, model_name: str):
    """Compare a task configuration to its expected model."""
    print("\n" + "=" * 80)
    print(f"COMPARING TASK TO MODEL: {crew_name}/{task_name} -> {model_name}")
    print("=" * 80)
    
    # Load task config
    tasks_file = (
        Path(__file__).parent 
        / "src" / "analyze_financial_reports" / "crews" / crew_name 
        / "config" / "tasks.yaml"
    )
    
    with open(tasks_file) as f:
        tasks = yaml.safe_load(f)
        task_config = tasks.get(task_name, {})
    
    print(f"\n📋 Task Configuration:")
    print(f"   Expected Output: {task_config.get('expected_output', 'N/A')}")
    
    # Load model
    from analyze_financial_reports import models
    model_class = getattr(models, model_name)
    schema = model_class.model_json_schema()
    
    print(f"\n📦 Model Schema ({model_name}):")
    if 'properties' in schema:
        print(f"   Required fields: {schema.get('required', [])}")
        print(f"   All fields: {list(schema['properties'].keys())}")
    
    print(f"\n✅ Checklist:")
    print(f"   [ ] Task describes all required model fields")
    print(f"   [ ] Task output format matches model structure")
    print(f"   [ ] Field names are consistent")


if __name__ == "__main__":
    print("\n🔍 CREW CONFIGURATION INSPECTOR\n")
    
    # Inspect each crew
    crews = [
        "question_generation_crew",
        "report_outline_crew",
        "research_section_crew",
        "report_writer_crew",
    ]
    
    for crew in crews:
        inspect_crew_config(crew)
        print("\n")
    
    # Inspect models
    inspect_models()
    
    # Compare specific task to model
    print("\n" * 2)
    print("🔎 SPECIFIC COMPARISONS:")
    compare_task_to_model(
        "question_generation_crew", 
        "extract_questions", 
        "QuestionsList"
    )
    compare_task_to_model(
        "report_outline_crew",
        "create_outline",
        "ReportOutline"
    )
    
    print("\n" + "=" * 80)
    print("✅ Inspection complete!")
    print("=" * 80 + "\n")
