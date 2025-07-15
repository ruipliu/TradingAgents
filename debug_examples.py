"""
TradingAgents Debug Examples

This file contains specific examples of how to use the debug functions.
Uncomment the sections you want to test.

Author: Debug Assistant
"""

import sys
import os
from pathlib import Path

# Ensure we're in the project root directory
project_root = Path(__file__).parent
os.chdir(project_root)

try:
    from debug import *
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Project root: {project_root}")
    print("\nPlease make sure you're in the project root directory and have installed dependencies:")
    print("cd /Users/ruipliu/repo/TradingAgents")
    print("pip install -r requirements.txt")
    print("python debug_examples.py")
    sys.exit(1)

def example_1_test_single_analyst():
    """Example 1: Test a single analyst with custom configuration."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Testing Single Market Analyst")
    print("="*60)
    
    # Create custom config for testing
    config = create_debug_config(
        llm_provider="openai",
        deep_model="gpt-4o-mini",
        quick_model="gpt-4o-mini",
        online_tools=True  # Set to False to use cached data
    )
    
    # Test market analyst
    result = test_market_analyst(
        ticker="AAPL",
        trade_date="2024-01-15",  # Use a past date
        config=config
    )
    
    # Inspect the result
    inspect_state(result, "Market Analyst Result")
    
    # Save result to file
    save_state_to_file(result, "market_analyst_result.json")

def example_2_test_all_analysts():
    """Example 2: Test all analysts sequentially."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Testing All Analysts")
    print("="*60)
    
    config = create_debug_config(
        online_tools=False,  # Use cached data for faster testing
        max_debate_rounds=1
    )
    
    # Test all analysts
    results = test_all_analysts(
        ticker="NVDA",
        trade_date="2024-01-15",
        config=config
    )
    
    # Show summary
    console.print("\n[bold green]Summary of Results:[/bold green]")
    for analyst, result in results.items():
        if "error" in result:
            console.print(f"  {analyst}: [red]Failed[/red]")
        else:
            report_key = f"{analyst}_report"
            if report_key in result and result[report_key]:
                console.print(f"  {analyst}: [green]Success[/green] ({len(result[report_key])} chars)")
            else:
                console.print(f"  {analyst}: [yellow]No report generated[/yellow]")

def example_3_test_research_team():
    """Example 3: Test research team debate."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Testing Research Team Debate")
    print("="*60)
    
    config = create_debug_config(
        max_debate_rounds=2,  # Allow more debate rounds
        online_tools=True
    )
    
    # First get analyst reports
    analyst_reports = test_all_analysts("TSLA", "2024-01-15", config)
    
    # Then test research team debate
    research_results = test_research_team_debate(
        ticker="TSLA",
        trade_date="2024-01-15",
        config=config,
        analyst_reports=analyst_reports
    )
    
    # Inspect the debate state
    if "investment_debate_state" in research_results:
        inspect_state(research_results["investment_debate_state"], "Research Debate State")

def example_4_test_full_workflow():
    """Example 4: Test complete workflow with minimal setup."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Testing Full Workflow")
    print("="*60)
    
    # Minimal config for faster testing
    config = create_debug_config(
        deep_model="gpt-4o-mini",
        quick_model="gpt-4o-mini",
        max_debate_rounds=1,
        max_risk_rounds=1,
        online_tools=True
    )
    
    # Test with just market analyst for speed
    final_state = test_full_workflow(
        ticker="AAPL",
        trade_date="2024-01-15",
        config=config,
        analysts=["market"]  # Just one analyst for testing
    )
    
    # Show final decision
    if "final_trade_decision" in final_state:
        console.print(Panel(
            final_state["final_trade_decision"],
            title="Final Trading Decision",
            border_style="green"
        ))

def example_5_test_streaming():
    """Example 5: Test streaming analysis with detailed output."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Testing Streaming Analysis")
    print("="*60)
    
    config = create_debug_config(
        online_tools=False,  # Use cached data
        max_debate_rounds=1
    )
    
    # Test streaming with market analyst only
    trace = test_streaming_analysis(
        ticker="AAPL",
        trade_date="2024-01-15",
        config=config,
        analysts=["market"]
    )
    
    console.print(f"\n[bold green]Streaming completed with {len(trace)} chunks[/bold green]")

def example_6_custom_configuration():
    """Example 6: Test with different LLM providers and configurations."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Testing Custom Configurations")
    print("="*60)
    
    # Test different configurations
    configs = [
        {
            "name": "OpenAI GPT-4o-mini",
            "config": create_debug_config(
                llm_provider="openai",
                deep_model="gpt-4o-mini",
                quick_model="gpt-4o-mini"
            )
        },
        # Add more configurations as needed
        # {
        #     "name": "Anthropic Claude",
        #     "config": create_debug_config(
        #         llm_provider="anthropic",
        #         deep_model="claude-3-haiku-20240307",
        #         quick_model="claude-3-haiku-20240307",
        #         backend_url="https://api.anthropic.com/"
        #     )
        # }
    ]
    
    for config_info in configs:
        console.print(f"\n[bold blue]Testing with {config_info['name']}[/bold blue]")
        try:
            result = test_market_analyst(
                ticker="AAPL",
                trade_date="2024-01-15",
                config=config_info["config"]
            )
            console.print(f"[green]✓ {config_info['name']} test successful[/green]")
        except Exception as e:
            console.print(f"[red]✗ {config_info['name']} test failed: {e}[/red]")

def example_7_state_inspection():
    """Example 7: Demonstrate state inspection utilities."""
    print("\n" + "="*60)
    print("EXAMPLE 7: State Inspection Utilities")
    print("="*60)
    
    config = create_debug_config()
    
    # Create initial state
    initial_state = create_initial_state("AAPL", "2024-01-15")
    inspect_state(initial_state, "Initial State")
    
    # Test market analyst and compare states
    result = test_market_analyst("AAPL", "2024-01-15", config)
    
    # Compare initial state with result
    compare_states(initial_state, result)

if __name__ == '__main__':
    """
    Uncomment the examples you want to run:
    """
    
    # Quick single analyst test
    example_1_test_single_analyst()
    
    # Test all analysts (takes longer)
    # example_2_test_all_analysts()
    
    # Test research team debate (requires analyst reports first)
    # example_3_test_research_team()
    
    # Test full workflow (takes longest)
    # example_4_test_full_workflow()
    
    # Test streaming analysis
    # example_5_test_streaming()
    
    # Test different configurations
    # example_6_custom_configuration()
    
    # Test state inspection utilities
    # example_7_state_inspection()
    
    console.print("\n[bold green]Debug examples completed![/bold green]")
    console.print("[dim]Uncomment other examples in the main section to test more features.[/dim]")
