#!/bin/bash
# Example commands for analyzing Jamaican Stock Exchange (JSE) companies

# Financial Services
echo "Analyzing NCB Financial Group (Financial Services)..."
python src/analyze_financial_reports/main.py \
  --company "NCB Financial Group" \
  --persona jse_dividend_investing

echo "Analyzing Sagicor Group Jamaica (Insurance/Financial)..."
python src/analyze_financial_reports/main.py \
  --company "Sagicor Group Jamaica" \
  --persona jse_dividend_investing

echo "Analyzing JMMB Group (Financial Services)..."
python src/analyze_financial_reports/main.py \
  --company "JMMB Group" \
  --persona value_investing

# Manufacturing & Distribution
echo "Analyzing Jamaica Broilers Group (Manufacturing)..."
python src/analyze_financial_reports/main.py \
  --company "Jamaica Broilers Group" \
  --persona growth_investing

echo "Analyzing GraceKennedy Limited (Conglomerate)..."
python src/analyze_financial_reports/main.py \
  --company "GraceKennedy Limited" \
  --persona garp_investing

echo "Analyzing Wisynco Group (Manufacturing/Distribution)..."
python src/analyze_financial_reports/main.py \
  --company "Wisynco Group" \
  --persona growth_investing

# Investment Companies
echo "Analyzing Proven Investments (Investment Company)..."
python src/analyze_financial_reports/main.py \
  --company "Proven Investments Limited" \
  --persona growth_investing

echo "Analyzing Mayberry Investments (Brokerage)..."
python src/analyze_financial_reports/main.py \
  --company "Mayberry Investments Limited" \
  --persona value_investing

# Other Notable Companies
echo "Analyzing Carreras Limited (Tobacco)..."
python src/analyze_financial_reports/main.py \
  --company "Carreras Limited" \
  --persona jse_dividend_investing

echo "Analyzing Lasco Manufacturing (Consumer Goods)..."
python src/analyze_financial_reports/main.py \
  --company "Lasco Manufacturing" \
  --persona growth_investing

echo "All JSE analyses complete!"
