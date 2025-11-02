#!/usr/bin/env python
"""
Quick test to verify the Pydantic models work correctly with the expected data formats.
This helps ensure the LLM will be able to populate them correctly.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from analyze_financial_reports.models import (
    FinancialData,
    CompletedSection,
)


def test_financial_data_model():
    """Test FinancialData model with different input formats."""
    print("=" * 80)
    print("Testing FinancialData Model")
    print("=" * 80)
    
    # Test 1: Correct format (JSON strings)
    print("\n✅ Test 1: Correct format (JSON strings)")
    try:
        data = FinancialData(
            section_title="Financial Overview",
            metrics=json.dumps({"revenue": 1000000, "eps": 5.2}),
            calculations=json.dumps({"pe_ratio": 15.5, "roe": 18.2}),
            visualizations=["charts/revenue_chart.png", "charts/profit_chart.png"],
            research_notes="Company shows strong fundamentals..."
        )
        print(f"   ✅ Success!")
        print(f"   Data: {data.model_dump()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: Empty strings (should work with defaults)
    print("\n✅ Test 2: Empty/default values")
    try:
        data = FinancialData(
            section_title="Market Analysis"
        )
        print(f"   ✅ Success!")
        print(f"   Data: {data.model_dump()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: What happens if LLM tries to pass dict instead of JSON string?
    print("\n✅ Test 3: Dict instead of JSON string (NOW WORKS WITH VALIDATOR!)")
    try:
        data = FinancialData(
            section_title="Test",
            metrics={"revenue": 1000000},  # This is a dict, validator converts it!
            calculations={"pe_ratio": 15.5},
        )
        print(f"   ✅ Success! Validator converted dicts to JSON strings")
        print(f"   Metrics type: {type(data.metrics)}")
        print(f"   Metrics value: {data.metrics}")
        print(f"   Calculations type: {type(data.calculations)}")
        print(f"   Calculations value: {data.calculations}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 4: Minimal valid data
    print("\n✅ Test 4: Minimal valid data")
    try:
        data = FinancialData(
            section_title="Risk Analysis",
            research_notes="No specific calculations needed for this qualitative section."
        )
        print(f"   ✅ Success!")
        print(f"   Metrics: '{data.metrics}'")
        print(f"   Calculations: '{data.calculations}'")
        print(f"   Visualizations: {data.visualizations}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")


def test_completed_section_model():
    """Test CompletedSection model."""
    print("\n" + "=" * 80)
    print("Testing CompletedSection Model")
    print("=" * 80)
    
    # Test 1: Correct format
    print("\n✅ Test 1: Correct format")
    try:
        section = CompletedSection(
            title="Executive Summary",
            content="""
# Executive Summary

This company shows strong performance across multiple metrics...

## Key Findings
- Revenue growth: 15%
- P/E ratio: 18.5
- Strong dividend history

## Conclusion
Based on our analysis...
            """,
            order=1
        )
        print(f"   ✅ Success!")
        print(f"   Title: {section.title}")
        print(f"   Content length: {len(section.content)} chars")
        print(f"   Order: {section.order}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: Very long content (realistic)
    print("\n✅ Test 2: Long content (800-1200 words)")
    try:
        long_content = "Word " * 1000  # Simulate 1000 words
        section = CompletedSection(
            title="Financial Analysis",
            content=long_content,
            order=2
        )
        print(f"   ✅ Success!")
        print(f"   Content length: {len(section.content)} chars")
    except Exception as e:
        print(f"   ❌ Failed: {e}")


def test_from_dict_creation():
    """Test creating models from dictionaries (how CrewAI returns them)."""
    print("\n" + "=" * 80)
    print("Testing Model Creation from Dicts (CrewAI format)")
    print("=" * 80)
    
    # Simulate what CrewAI might return
    print("\n✅ Test: FinancialData from dict")
    crew_output = {
        "section_title": "Profitability Analysis",
        "metrics": '{"gross_margin": 45.2, "net_margin": 22.1}',
        "calculations": '{"roe": 18.5, "roa": 12.3}',
        "visualizations": ["chart1.png"],
        "research_notes": "The company demonstrates strong profitability..."
    }
    
    try:
        data = FinancialData(**crew_output)
        print(f"   ✅ Success!")
        print(f"   Created from dict: {data.model_dump()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\n✅ Test: CompletedSection from dict")
    crew_output = {
        "title": "Market Position",
        "content": "# Market Position\n\nThe company holds a strong position...",
        "order": 3
    }
    
    try:
        section = CompletedSection(**crew_output)
        print(f"   ✅ Success!")
        print(f"   Created from dict: {section.model_dump()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")


def test_json_serialization():
    """Test JSON serialization/deserialization."""
    print("\n" + "=" * 80)
    print("Testing JSON Serialization")
    print("=" * 80)
    
    print("\n✅ Test: FinancialData JSON round-trip")
    try:
        original = FinancialData(
            section_title="Test",
            metrics='{"key": "value"}',
            calculations='{"calc": 123}',
            visualizations=["chart.png"],
            research_notes="Notes here"
        )
        
        # To JSON string
        json_str = original.model_dump_json()
        print(f"   JSON string: {json_str}")
        
        # From JSON string
        loaded = FinancialData.model_validate_json(json_str)
        print(f"   ✅ Round-trip successful!")
        print(f"   Original == Loaded: {original == loaded}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")


if __name__ == "__main__":
    print("\n🧪 TESTING PYDANTIC MODELS\n")
    
    test_financial_data_model()
    test_completed_section_model()
    test_from_dict_creation()
    test_json_serialization()
    
    print("\n" + "=" * 80)
    print("✅ All model tests completed!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  • FinancialData requires metrics/calculations as JSON STRINGS")
    print("  • Use json.dumps() to convert dicts to strings")
    print("  • Models can be created from dicts (CrewAI format)")
    print("  • All fields have sensible defaults")
    print("\n")
