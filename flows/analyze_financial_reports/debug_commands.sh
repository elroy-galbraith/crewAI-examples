#!/bin/bash
# Quick debugging commands for the financial reports flow
# Usage: source debug_commands.sh (to load these as functions)
#    or: bash debug_commands.sh [command_name]

# Activate environment (needed for all commands)
activate_env() {
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
    echo "✅ Environment activated"
}

# Test 1: Verify tools work independently
test_tools() {
    echo "🔧 Testing tools independently..."
    activate_env
    python test_tools.py
}

# Test 2: Test single crew
test_crew() {
    echo "🔧 Testing single crew..."
    activate_env
    python test_single_crew.py
}

# Test 3: Inspect configurations
inspect_configs() {
    echo "🔧 Inspecting configurations..."
    activate_env
    python inspect_config.py
}

# Test 4: Debug question generation only
debug_questions() {
    echo "🔧 Debugging question generation..."
    activate_env
    python debug_flow.py --step questions --verbose
}

# Test 5: Debug outline generation only
debug_outline() {
    echo "🔧 Debugging outline generation..."
    activate_env
    python debug_flow.py --step outline --verbose
}

# Test 6: Debug research step only
debug_research() {
    echo "🔧 Debugging research step..."
    activate_env
    python debug_flow.py --step research --verbose
}

# Test 7: Debug all steps
debug_all() {
    echo "🔧 Debugging all steps..."
    activate_env
    python debug_flow.py --step all --verbose
}

# Test 8: Trace full flow
trace_flow() {
    local company="${1:-Apple Inc.}"
    local persona="${2:-value_investing}"
    echo "🔧 Tracing flow for $company with $persona strategy..."
    activate_env
    python trace_flow.py --company "$company" --persona "$persona"
}

# Test 9: Run actual flow with debugging
run_flow() {
    local company="${1:-Apple Inc.}"
    local persona="${2:-value_investing}"
    echo "🔧 Running flow for $company with $persona strategy..."
    activate_env
    python src/analyze_financial_reports/main.py --company "$company" --persona "$persona"
}

# Show help
show_help() {
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║                    CrewAI Flow Debugging Commands                         ║
╚═══════════════════════════════════════════════════════════════════════════╝

Quick Start (run in order):
  1. test_tools          → Verify tools work independently
  2. test_crew           → Test a single crew
  3. inspect_configs     → Check configuration files
  4. debug_all           → Debug entire flow step-by-step

Individual Stage Debugging:
  debug_questions        → Test question generation only
  debug_outline          → Test outline creation only
  debug_research         → Test research stage only
  debug_all              → Test all stages with validation

Full Execution:
  trace_flow [company] [persona]     → Run with detailed logging
  run_flow [company] [persona]       → Run actual flow

Examples:
  test_tools                          # Test tools first
  debug_questions                     # Debug just questions
  trace_flow "Microsoft" "growth_investing"
  run_flow "Tesla Inc." "growth_investing"

Available Personas:
  - value_investing (default)
  - growth_investing
  - dividend_investing
  - garp_investing
  - jse_dividend_investing

Usage:
  source debug_commands.sh            # Load functions
  test_tools                          # Run command

  OR

  bash debug_commands.sh test_tools   # Run directly

╚═══════════════════════════════════════════════════════════════════════════╝
EOF
}

# If script is run directly (not sourced), execute the command
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -eq 0 ]; then
        show_help
    else
        "$@"
    fi
fi
