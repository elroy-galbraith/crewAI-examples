"""
Example Investment Personas

This directory contains pre-configured investment strategy personas that can be
used with the Financial Report Flow.

Available Personas:
- value_investing.yaml: Classic value investing approach (low P/E, P/B, high dividends)
- growth_investing.yaml: Growth-focused strategy (high growth rates, expanding markets)
- dividend_investing.yaml: Income-focused strategy (high yields, dividend growth)
- garp_investing.yaml: Growth at Reasonable Price (balanced growth and valuation)

Usage:
------
To use a persona in your flow, load it and convert to InvestmentPersona:

```python
import yaml
from analyze_financial_reports.types import InvestmentPersona

# Load persona from YAML
with open('config/investment_personas/value_investing.yaml') as f:
    persona_data = yaml.safe_load(f)

# Create InvestmentPersona
persona = InvestmentPersona(**persona_data)

# Use in ReportState
state = ReportState(
    company_name="Apple Inc.",
    investment_persona=persona
)
```

Customizing Personas:
--------------------
You can create custom personas by:
1. Copying an existing YAML file
2. Modifying the criteria, metrics, and philosophy
3. Adjusting risk tolerance and time horizon
4. Loading it in your flow

The persona guides:
- What questions the Portfolio Manager asks
- Which metrics the analysts focus on
- How the final score is calculated
- What makes a "good" vs "bad" investment
"""
