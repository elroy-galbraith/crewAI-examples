#!/bin/bash
# Activation script for analyze_financial_reports virtual environment
# Usage: source activate.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"

echo "✅ Virtual environment activated!"
echo "📍 Project: analyze_financial_reports"
echo "🐍 Python: $(python --version)"
echo ""
echo "Quick commands:"
echo "  • List personas: python src/analyze_financial_reports/main.py --list-personas"
echo "  • Run analysis: python src/analyze_financial_reports/main.py -c 'COMPANY' -p PERSONA"
echo "  • Deactivate: deactivate"
