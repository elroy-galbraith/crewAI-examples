# Analyze Financial Reports Flow

An AI-powered financial analysis system built with [CrewAI](https://crewai.com) that generates comprehensive investment reports through multi-agent collaboration. This flow simulates the research and analysis process of a professional investment team.

**✨ Works with companies from any stock exchange** - NYSE, NASDAQ, JSE (Jamaica), LSE (London), TSX (Toronto), ASX (Australia), and more!

## Overview

This flow automates the creation of detailed financial analysis reports by orchestrating multiple AI crews, each specializing in different aspects of financial analysis. The system is designed around a specific investment strategy/persona and produces reports that evaluate companies against defined investment criteria.

### The Five-Stage Analysis Process

1. **Generate Research Questions** 
   - Simulates a conversation between a Portfolio Manager and Financial Analyst
   - Generates targeted research questions based on the investment strategy
   - Questions cover industry analysis, financial metrics, growth prospects, valuation, and risks

2. **Create Report Outline**
   - Organizes research questions into a structured report outline
   - Defines sections with clear objectives
   - Specifies which analytical tools are needed for each section

3. **Research Sections (Parallel)**
   - Multiple crews work simultaneously to research each section
   - Uses Financial Report RAG, web search, and other tools
   - Gathers data, performs calculations, creates visualizations

4. **Write Sections (Parallel)**
   - Multiple crews write report sections concurrently
   - Transforms research data into professional analysis
   - Maintains consistency with investment strategy criteria

5. **Compile and Score**
   - Combines all sections into a complete report
   - Applies LLM-based deduplication
   - Scores the company against investment criteria
   - Generates final recommendation (Strong Buy, Buy, Hold, Sell, Strong Sell)

## Features

### Custom Financial Tools

- **Financial Report RAG Tool**: Retrieves information from 10-K, 10-Q, and annual reports using semantic search
- **Ratio Calculator**: Computes key financial ratios (P/E, P/B, ROE, ROA, Current Ratio, Debt-to-Equity, etc.)
- **Visualization Tool**: Creates charts and graphs to visualize financial trends
- **Web Search**: Gathers market context and industry information

### Investment Strategy Support

The system supports various investment strategies with customizable criteria:
- Value Investing
- Growth Investing
- Dividend/Income Investing
- GARP (Growth at a Reasonable Price)
- Custom strategies with user-defined metrics

### Parallel Processing

Research and writing stages execute in parallel, dramatically reducing report generation time:
- 5 sections → 5 parallel research crews
- 5 sections → 5 parallel writing crews

## Installation

### Prerequisites

- **Python 3.10, 3.11, or 3.12** (NOT 3.13)
- **macOS 13+ recommended** (macOS 12 compatible with latest CrewAI)
- **uv** package manager (recommended) or pip

⚠️ **Important:** If you have Python 3.13, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for downgrade instructions.

### Quick Setup (5 minutes)

See **[SETUP.md](SETUP.md)** for a quick start guide!

Or follow these steps:

1. **Navigate to the project directory:**
```bash
cd flows/analyze_financial_reports
```

2. **Create a virtual environment with Python 3.12:**
```bash
# Using uv (recommended)
uv venv --python 3.12 .venv

# Or using standard venv
python3.12 -m venv .venv
```

3. **Activate the virtual environment:**
```bash
# Quick activation (recommended)
source activate.sh

# Or manually
source .venv/bin/activate
```

4. **Install dependencies:**
```bash
# Using uv (faster)
uv pip install -e .

# Or using pip
pip install -e .
```

5. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
- `OPENAI_API_KEY` - Required for GPT-4 
- `SERPER_API_KEY` - Required for web search

## Usage

### Quick Start

The easiest way to run the flow with custom company and strategy:

```bash
# Analyze Microsoft with Growth strategy
python src/analyze_financial_reports/main.py --company "Microsoft Corporation" --persona growth_investing

# Analyze Tesla with default Value strategy
python src/analyze_financial_reports/main.py --company "Tesla Inc."

# Analyze Apple (default) with Dividend strategy
python src/analyze_financial_reports/main.py --persona dividend_investing

# Use all defaults (Apple Inc. with Value Investing)
python src/analyze_financial_reports/main.py
```

### List Available Investment Strategies

```bash
python src/analyze_financial_reports/main.py --list-personas
```

### Using CrewAI CLI

Alternatively, use the CrewAI CLI (analyzes default company/strategy):

```bash
crewai flow kickoff
```

This will:
1. Generate research questions for the configured company
2. Create a report outline
3. Research all sections in parallel
4. Write all sections in parallel
5. Compile the final report with a score

The report will be saved as a markdown file in the project directory.

### For Complete Usage Instructions

See **[USAGE.md](USAGE.md)** for detailed documentation on:
- All 4 ways to specify company and persona
- Creating custom investment strategies
- Programmatic usage
- Environment variable configuration
- Examples for different use cases

### Visualizing the Flow

To see the flow structure:

```bash
python src/analyze_financial_reports/main.py --plot
```

### Available Investment Strategies

- **value_investing** - Low P/E, P/B, high dividends (Low risk, Long-term)
- **growth_investing** - High growth rates, market expansion (Medium-High risk, Long-term)
- **dividend_investing** - Income focus, dividend safety (Low risk, Long-term)
- **garp_investing** - Balanced growth and value (Medium risk, Medium-to-Long-term)

### Example Usage Scenarios

```bash
# Tech stock growth analysis
python src/analyze_financial_reports/main.py -c "NVIDIA" -p growth_investing

# Dividend stock analysis
python src/analyze_financial_reports/main.py -c "Johnson & Johnson" -p dividend_investing

# Value opportunity
python src/analyze_financial_reports/main.py -c "Bank of America" -p value_investing

# Balanced approach
python src/analyze_financial_reports/main.py -c "Costco" -p garp_investing
```

### Customizing the Analysis (Advanced)

#### Creating Custom Investment Strategies

1. Copy an existing persona file:
```bash
cp src/analyze_financial_reports/config/investment_personas/value_investing.yaml \
   src/analyze_financial_reports/config/investment_personas/my_strategy.yaml
```

2. Edit the criteria and metrics in the YAML file

3. Use it:
```bash
python src/analyze_financial_reports/main.py -c "Apple Inc." -p my_strategy
```

#### Programmatic Usage

If you're using the flow in your own Python code:

```python
from analyze_financial_reports.main import kickoff

# Analyze any company with any strategy
kickoff(company="Amazon.com Inc.", persona="growth_investing")
```

For more advanced usage, see [USAGE.md](USAGE.md).

## Project Structure
        key_metrics=["Revenue Growth", "EPS Growth", "P/E Ratio", "PEG Ratio"],
        criteria={
            "min_revenue_growth": 15,
            "min_eps_growth": 20,
            "max_pe": 30,
            "max_peg": 2.0,
        },
        risk_tolerance="medium",
        time_horizon="long-term",
    )
)
```

#### Use Custom Investment Personas

See `src/analyze_financial_reports/config/investment_personas/` for examples:
- `value_investing.yaml`
- `growth_investing.yaml`
- `dividend_investing.yaml`
- `garp_investing.yaml`
- `jse_dividend_investing.yaml` - Adapted for Jamaican Stock Exchange

## International Stock Exchanges

This flow works with companies from **any stock exchange**:

- **🇺🇸 US:** NYSE, NASDAQ (Apple, Microsoft, Tesla, etc.)
- **🇯🇲 Jamaica:** JSE (NCB Financial, Sagicor, GraceKennedy, etc.) - See **[JSE_GUIDE.md](JSE_GUIDE.md)**
- **🇬🇧 UK:** LSE (HSBC, BP, Unilever, etc.)
- **🇨🇦 Canada:** TSX (Royal Bank, Shopify, etc.)
- **🇦🇺 Australia:** ASX (BHP, Commonwealth Bank, etc.)
- **And more!**

The flow adapts to different:
- Currencies (USD, JMD, GBP, CAD, AUD, etc.)
- Regulatory frameworks (SEC, JSE, FCA, etc.)
- Market characteristics (liquidity, volatility, etc.)
- Reporting standards (GAAP, IFRS, etc.)

**For JSE companies specifically**, see the complete guide: **[JSE_GUIDE.md](JSE_GUIDE.md)**

## Project Structure

```
analyze_financial_reports/
├── src/
│   └── analyze_financial_reports/
│       ├── main.py                 # Main flow orchestration
│       ├── types.py                # Pydantic data models
│       ├── tools/                  # Custom financial tools
│       │   └── financial_tools.py
│       ├── crews/                  # Specialized AI crews
│       │   ├── question_generation_crew/
│       │   │   ├── question_generation_crew.py
│       │   │   └── config/
│       │   │       ├── agents.yaml
│       │   │       └── tasks.yaml
│       │   ├── report_outline_crew/
│       │   ├── research_section_crew/
│       │   └── report_writer_crew/
│       └── config/
│           └── investment_personas/
├── pyproject.toml
├── .env.example
└── README.md
```

## How It Works

### Flow Architecture

The `FinancialReportFlow` manages state through the `ReportState` class and orchestrates five crews:

1. **QuestionGenerationCrew**: Portfolio Manager + Analyst agents simulate a conversation
2. **ReportOutlineCrew**: Research Planner organizes questions into sections
3. **ResearchSectionCrew**: Financial Researcher + Data Analyst gather and analyze data
4. **ReportWriterCrew**: Report Writer creates polished sections
5. **Scoring Logic**: LLM-based evaluation against investment criteria

### Data Flow

```
Company Name + Investment Strategy
    ↓
Research Questions (QuestionsList)
    ↓
Report Outline (ReportOutline)
    ↓
Research Data (List[FinancialData]) ← Parallel Processing
    ↓
Report Sections (List[CompletedSection]) ← Parallel Processing
    ↓
Final Report + Company Score
```

### Agent Roles

- **Portfolio Manager**: Asks strategic investment questions
- **Financial Analyst**: Helps formulate research approach
- **Research Planner**: Organizes analysis structure
- **Financial Researcher**: Gathers data from reports and web
- **Data Analyst**: Performs calculations and creates visualizations
- **Report Writer**: Transforms analysis into professional narrative

## Advanced Features

### Implementing the RAG Tool

To connect real financial data, implement the `FinancialReportRAGTool`:

```python
# In tools/financial_tools.py
def _run(self, company_name: str, query: str) -> str:
    # 1. Connect to vector database (ChromaDB, Pinecone, etc.)
    # 2. Embed the query
    # 3. Search for relevant document chunks
    # 4. Return context with citations
    pass
```

### Adding New Financial Ratios

Extend the `RatioCalculatorTool` in `tools/financial_tools.py`:

```python
elif ratio_type == "PEG_RATIO":
    pe = financial_data.get("pe", 0)
    growth_rate = financial_data.get("growth_rate", 0)
    if growth_rate != 0:
        result["value"] = round(pe / growth_rate, 2)
        result["formula"] = "P/E Ratio / Growth Rate"
```

### Custom Visualizations

Implement actual chart generation in `VisualizationTool`:

```python
import matplotlib.pyplot as plt

def _run(self, data, chart_type, title, filename):
    plt.figure(figsize=(10, 6))
    
    if chart_type == "line":
        plt.plot(data['labels'], data['values'])
    elif chart_type == "bar":
        plt.bar(data['labels'], data['values'])
    
    plt.title(title)
    plt.savefig(f"./visualizations/{filename}.png")
    plt.close()
    
    return f"./visualizations/{filename}.png"
```

## Comparison with write_a_book_with_flows

| Aspect | write_a_book_with_flows | analyze_financial_reports |
|--------|------------------------|---------------------------|
| **Purpose** | Generate books | Generate financial reports |
| **Initial Input** | Topic + Goal | Company + Investment Strategy |
| **Stage 1** | Generate outline | Generate research questions |
| **Stage 2** | (none) | Create report outline |
| **Stage 3** | Write chapters (parallel) | Research sections (parallel) |
| **Stage 4** | (none) | Write sections (parallel) |
| **Stage 5** | Compile book | Compile + Score company |
| **Crews** | 2 crews | 4 crews |
| **Tools** | Web search | RAG, Ratio Calculator, Visualization, Web search |
| **Output** | Book (markdown) | Report + Score (markdown) |

## Future Enhancements

- [ ] Integrate real vector database for RAG
- [ ] Add support for real-time financial data APIs
- [ ] Implement advanced deduplication with LLM
- [ ] Add comparative analysis (multiple companies)
- [ ] Create interactive dashboards
- [ ] Support for different report formats (PDF, HTML)
- [ ] Historical backtesting of investment scores

## Support

For support, questions, or feedback:

- Visit the [CrewAI documentation](https://docs.crewai.com)
- Check out the [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with docs](https://chatg.pt/DWjSBZn)

## License

MIT License - See LICENSE file for details

---

Built with ❤️ using CrewAI
