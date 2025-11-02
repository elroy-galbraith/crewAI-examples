#!/usr/bin/env python
"""
Simple script to test tools and validate outputs independently.
This helps debug function calling and output format issues.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from analyze_financial_reports.tools.financial_tools import (
    FinancialReportRAGTool,
    RatioCalculatorTool,
)


def test_rag_tool():
    """Test the Financial Report RAG Tool."""
    print("=" * 80)
    print("Testing Financial Report RAG Tool")
    print("=" * 80)
    
    tool = FinancialReportRAGTool()
    
    print(f"\nTool Name: {tool.name}")
    print(f"Tool Description: {tool.description}")
    print(f"Input Schema: {tool.args_schema.model_json_schema()}")
    
    # Test execution
    print("\n--- Test 1: Basic Query ---")
    try:
        result = tool._run(
            company_name="Apple Inc.",
            query="What was the revenue for the latest quarter?"
        )
        print(f"✅ Success! Result length: {len(result)} chars")
        print(f"Result preview:\n{result[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with different inputs
    print("\n--- Test 2: Different Query ---")
    try:
        result = tool._run(
            company_name="Microsoft",
            query="What is the profit margin?"
        )
        print(f"✅ Success! Result length: {len(result)} chars")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_ratio_calculator():
    """Test the Ratio Calculator Tool."""
    print("\n" + "=" * 80)
    print("Testing Ratio Calculator Tool")
    print("=" * 80)
    
    tool = RatioCalculatorTool()
    
    print(f"\nTool Name: {tool.name}")
    print(f"Tool Description: {tool.description}")
    print(f"Input Schema: {tool.args_schema.model_json_schema()}")
    
    # Test P/E ratio
    print("\n--- Test 1: P/E Ratio ---")
    try:
        result = tool._run(
            financial_data={"price": 150.0, "eps": 6.0},
            ratio_type="PE"
        )
        print(f"✅ Success!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test P/B ratio
    print("\n--- Test 2: P/B Ratio ---")
    try:
        result = tool._run(
            financial_data={"price": 150.0, "book_value_per_share": 20.0},
            ratio_type="PB"
        )
        print(f"✅ Success!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test with missing data
    print("\n--- Test 3: Missing Data (should handle gracefully) ---")
    try:
        result = tool._run(
            financial_data={"price": 150.0},  # Missing EPS
            ratio_type="PE"
        )
        print(f"✅ Tool handled missing data")
        print(f"Result: {result}")
    except Exception as e:
        print(f"⚠️  Error (expected): {e}")


def test_model_formats():
    """Test model serialization formats."""
    print("\n" + "=" * 80)
    print("Testing Model Formats")
    print("=" * 80)
    
    from analyze_financial_reports.models import (
        ResearchQuestion,
        ReportSection,
        InvestmentPersona,
        FinancialData,
    )
    import json
    
    # Test ResearchQuestion
    print("\n--- ResearchQuestion ---")
    q = ResearchQuestion(
        question="What is the P/E ratio?",
        category="Financial Ratios",
        priority="high"
    )
    print(f"Dict: {q.model_dump()}")
    print(f"JSON: {q.model_dump_json()}")
    
    # Test ReportSection
    print("\n--- ReportSection ---")
    section = ReportSection(
        title="Financial Overview",
        description="Analysis of key metrics",
        required_tools=["financial_rag", "ratio_calculator"],
        order=1
    )
    print(f"Dict: {section.model_dump()}")
    print(f"JSON: {section.model_dump_json()}")
    
    # Test InvestmentPersona
    print("\n--- InvestmentPersona ---")
    persona = InvestmentPersona(
        name="Value Investing",
        strategy_type="Value",
        key_metrics=["P/E", "P/B"],
        criteria=json.dumps({"max_pe": 15}),
        risk_tolerance="low",
        time_horizon="long-term"
    )
    print(f"Dict: {persona.model_dump()}")
    print(f"JSON (formatted): {persona.model_dump_json(indent=2)}")
    
    # Test FinancialData
    print("\n--- FinancialData ---")
    data = FinancialData(
        section_title="Test Section",
        metrics=json.dumps({"revenue": 100000}),
        calculations=json.dumps({"pe_ratio": 15.5}),
        visualizations=["chart1.png"],
        research_notes="Sample notes"
    )
    print(f"Dict: {data.model_dump()}")
    print(f"JSON: {data.model_dump_json()}")


if __name__ == "__main__":
    print("\n🔧 TESTING CREWAI TOOLS AND MODELS\n")
    
    # Run all tests
    test_rag_tool()
    test_ratio_calculator()
    test_model_formats()
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80 + "\n")
