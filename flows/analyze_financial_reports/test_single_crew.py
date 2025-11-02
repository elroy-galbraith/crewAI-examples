#!/usr/bin/env python
"""
Minimal test script to run a single crew and inspect its output.
This is the simplest way to debug function calling and output format issues.

Usage:
    python test_single_crew.py
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_question_crew():
    """Test just the question generation crew."""
    print("=" * 80)
    print("TESTING QUESTION GENERATION CREW")
    print("=" * 80)
    
    from analyze_financial_reports.crews.question_generation_crew.question_generation_crew import (
        QuestionGenerationCrew,
    )
    from analyze_financial_reports.main import get_default_persona
    
    # Set up inputs
    company = "Apple Inc."
    persona = get_default_persona()
    
    inputs = {
        "company_name": company,
        "investment_strategy": persona.strategy_type,
        "investment_persona": persona.model_dump_json(indent=2),
    }
    
    print(f"\n📋 Inputs:")
    print(f"  Company: {company}")
    print(f"  Strategy: {persona.strategy_type}")
    print(f"\n🚀 Running crew...\n")
    
    try:
        # Create and run the crew
        crew = QuestionGenerationCrew()
        output = crew.crew().kickoff(inputs=inputs)
        
        print("\n" + "=" * 80)
        print("✅ CREW COMPLETED")
        print("=" * 80)
        
        # Inspect the output
        print(f"\n📊 Output Type: {type(output)}")
        
        if isinstance(output, dict):
            print(f"📊 Output Keys: {list(output.keys())}")
            
            # Check for 'questions' key
            if 'questions' in output:
                questions = output['questions']
                print(f"\n✅ Found 'questions' key")
                print(f"   Number of questions: {len(questions)}")
                print(f"   Questions type: {type(questions)}")
                
                # Print each question
                print(f"\n📝 Questions:")
                for i, q in enumerate(questions, 1):
                    print(f"\n  {i}. Type: {type(q)}")
                    if hasattr(q, 'question'):
                        print(f"     Question: {q.question}")
                        print(f"     Category: {q.category}")
                        print(f"     Priority: {q.priority}")
                    else:
                        print(f"     Content: {q}")
            else:
                print(f"\n❌ 'questions' key not found in output")
            
            # Print full output for debugging
            print(f"\n📄 Full Output (JSON):")
            print(json.dumps(output, indent=2, default=str))
        else:
            print(f"\n⚠️  Output is not a dictionary")
            print(f"Output: {output}")
        
        return output
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_with_mock_data():
    """Test crew behavior with mock/minimal data to isolate issues."""
    print("\n" + "=" * 80)
    print("TESTING WITH MOCK DATA (No LLM calls)")
    print("=" * 80)
    
    from analyze_financial_reports.models import ResearchQuestion, QuestionsList
    
    # Create mock questions manually
    print("\n📋 Creating mock ResearchQuestion objects...")
    
    q1 = ResearchQuestion(
        question="What is the P/E ratio?",
        category="Financial Ratios",
        priority="high"
    )
    
    q2 = ResearchQuestion(
        question="What is revenue growth?",
        category="Growth Metrics",
        priority="medium"
    )
    
    questions_list = QuestionsList(questions=[q1, q2])
    
    print(f"✅ Created {len(questions_list.questions)} questions")
    
    # Test serialization
    print(f"\n📄 Testing Pydantic serialization:")
    print(f"   Dict format: {questions_list.model_dump()}")
    print(f"   JSON format: {questions_list.model_dump_json(indent=2)}")
    
    # Test that this matches what crew should output
    print(f"\n📊 Expected crew output format:")
    expected_output = {
        "questions": questions_list.questions
    }
    print(f"   {expected_output}")


if __name__ == "__main__":
    print("\n🧪 MINIMAL CREW TESTING\n")
    
    # Test with mock data first (no API calls)
    test_with_mock_data()
    
    # Then test actual crew
    print("\n" * 2)
    response = input("Run actual crew with LLM? This will make API calls. (y/N): ")
    
    if response.lower() == 'y':
        test_question_crew()
    else:
        print("\nSkipped actual crew test.")
    
    print("\n✅ Testing complete!\n")
