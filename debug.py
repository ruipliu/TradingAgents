"""
TradingAgents Debug Module

This module provides comprehensive debugging and testing functions for the TradingAgentsGraph.
Use this to test individual components, analyze intermediate states, and debug the full workflow.

Usage:
    python debug.py

Author: Debug Assistant
"""

import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import box

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.agents.utils.agent_states import AgentState, InvestDebateState, RiskDebateState

console = Console()

# =============================================================================
# CONFIGURATION FUNCTIONS
# =============================================================================

def create_debug_config(
    llm_provider: str = "google",
    deep_model: str = "gemini-2.5-pro",
    quick_model: str = "gemini-2.5-flash",
    backend_url: str = "https://generativelanguage.googleapis.com/v1beta",
    max_debate_rounds: int = 1,
    max_risk_rounds: int = 1,
    online_tools: bool = True
) -> Dict[str, Any]:
    """
    Create a debug configuration for testing.

    Args:
        llm_provider: LLM provider ("openai", "anthropic", "google", "ollama", "openrouter")
        deep_model: Model for deep thinking tasks
        quick_model: Model for quick thinking tasks
        backend_url: API endpoint URL
        max_debate_rounds: Number of debate rounds for research team
        max_risk_rounds: Number of debate rounds for risk team
        online_tools: Whether to use online tools or cached data

    Returns:
        Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    config.update({
        "llm_provider": llm_provider.lower(),
        "deep_think_llm": deep_model,
        "quick_think_llm": quick_model,
        "backend_url": backend_url,
        "max_debate_rounds": max_debate_rounds,
        "max_risk_discuss_rounds": max_risk_rounds,
        "online_tools": online_tools,
    })
    return config

def print_config_info(config: Dict[str, Any]):
    """Print configuration information in a nice format."""
    table = Table(title="Debug Configuration", box=box.ROUNDED)
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    key_settings = [
        "llm_provider", "deep_think_llm", "quick_think_llm",
        "backend_url", "max_debate_rounds", "max_risk_discuss_rounds",
        "online_tools"
    ]

    for key in key_settings:
        if key in config:
            table.add_row(key, str(config[key]))

    console.print(table)

# =============================================================================
# GRAPH INITIALIZATION FUNCTIONS
# =============================================================================

def create_debug_graph(
    analysts: List[str] = ["market"],
    config: Optional[Dict[str, Any]] = None
) -> TradingAgentsGraph:
    """
    Create a TradingAgentsGraph for debugging.

    Args:
        analysts: List of analyst types to include
                 Options: ["market", "social", "news", "fundamentals"]
        config: Configuration dictionary (uses debug config if None)

    Returns:
        Initialized TradingAgentsGraph
    """
    if config is None:
        config = create_debug_config()

    console.print(f"[bold blue]Creating TradingAgentsGraph with analysts: {analysts}[/bold blue]")
    print_config_info(config)

    try:
        graph = TradingAgentsGraph(
            selected_analysts=analysts,
            config=config,
            debug=True
        )
        console.print("[bold green]✓ Graph created successfully![/bold green]")
        return graph
    except Exception as e:
        console.print(f"[bold red]✗ Error creating graph: {e}[/bold red]")
        raise

def create_initial_state(
    ticker: str = "AAPL",
    trade_date: str = None
) -> Dict[str, Any]:
    """
    Create initial state for testing.

    Args:
        ticker: Stock ticker symbol
        trade_date: Trading date (YYYY-MM-DD format, defaults to yesterday)

    Returns:
        Initial state dictionary
    """
    if trade_date is None:
        # Use yesterday's date to avoid future date issues
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        trade_date = yesterday.strftime("%Y-%m-%d")

    # Create a temporary graph to get the initial state structure
    temp_graph = create_debug_graph(["market"])
    initial_state = temp_graph.propagator.create_initial_state(ticker, trade_date)

    console.print(f"[bold blue]Created initial state for {ticker} on {trade_date}[/bold blue]")
    return initial_state

# =============================================================================
# INDIVIDUAL AGENT TESTING FUNCTIONS
# =============================================================================

def test_market_analyst(
    ticker: str = "AAPL",
    trade_date: str = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Test the Market Analyst individually.

    Args:
        ticker: Stock ticker to analyze
        trade_date: Date for analysis
        config: Configuration to use

    Returns:
        Market analyst result state
    """
    console.print(Panel("[bold cyan]Testing Market Analyst[/bold cyan]", expand=False))

    # Create graph with only market analyst
    graph = create_debug_graph(["market"], config)
    initial_state = create_initial_state(ticker, trade_date)

    # Get the market analyst node
    market_node = graph.graph_setup.setup_graph(["market"]).nodes["market"]

    console.print(f"[yellow]Running market analysis for {ticker}...[/yellow]")

    try:
        result = market_node(initial_state)

        # Display results
        if result.get("market_report"):
            console.print(Panel(
                Markdown(result["market_report"]),
                title="Market Analysis Report",
                border_style="green"
            ))

        # Display tool calls if any
        if result.get("messages") and hasattr(result["messages"][-1], "tool_calls"):
            tool_calls = result["messages"][-1].tool_calls
            if tool_calls:
                console.print(f"[blue]Tool calls made: {len(tool_calls)}[/blue]")
                for i, call in enumerate(tool_calls):
                    console.print(f"  {i+1}. {call.get('name', 'Unknown tool')}")

        return result

    except Exception as e:
        console.print(f"[bold red]✗ Error in market analyst: {e}[/bold red]")
        raise

def test_social_analyst(
    ticker: str = "AAPL",
    trade_date: str = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Test the Social Media Analyst individually.

    Args:
        ticker: Stock ticker to analyze
        trade_date: Date for analysis
        config: Configuration to use

    Returns:
        Social analyst result state
    """
    console.print(Panel("[bold cyan]Testing Social Media Analyst[/bold cyan]", expand=False))

    # Create graph with only social analyst
    graph = create_debug_graph(["social"], config)
    initial_state = create_initial_state(ticker, trade_date)

    # Get the social analyst node
    social_node = graph.graph_setup.setup_graph(["social"]).nodes["social"]

    console.print(f"[yellow]Running social sentiment analysis for {ticker}...[/yellow]")

    try:
        result = social_node(initial_state)

        # Display results
        if result.get("sentiment_report"):
            console.print(Panel(
                Markdown(result["sentiment_report"]),
                title="Social Sentiment Report",
                border_style="green"
            ))

        # Display tool calls if any
        if result.get("messages") and hasattr(result["messages"][-1], "tool_calls"):
            tool_calls = result["messages"][-1].tool_calls
            if tool_calls:
                console.print(f"[blue]Tool calls made: {len(tool_calls)}[/blue]")
                for i, call in enumerate(tool_calls):
                    console.print(f"  {i+1}. {call.get('name', 'Unknown tool')}")

        return result

    except Exception as e:
        console.print(f"[bold red]✗ Error in social analyst: {e}[/bold red]")
        raise

def test_news_analyst(
    ticker: str = "AAPL",
    trade_date: str = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Test the News Analyst individually.

    Args:
        ticker: Stock ticker to analyze
        trade_date: Date for analysis
        config: Configuration to use

    Returns:
        News analyst result state
    """
    console.print(Panel("[bold cyan]Testing News Analyst[/bold cyan]", expand=False))

    # Create graph with only news analyst
    graph = create_debug_graph(["news"], config)
    initial_state = create_initial_state(ticker, trade_date)

    # Get the news analyst node
    news_node = graph.graph_setup.setup_graph(["news"]).nodes["news"]

    console.print(f"[yellow]Running news analysis for {ticker}...[/yellow]")

    try:
        result = news_node(initial_state)

        # Display results
        if result.get("news_report"):
            console.print(Panel(
                Markdown(result["news_report"]),
                title="News Analysis Report",
                border_style="green"
            ))

        # Display tool calls if any
        if result.get("messages") and hasattr(result["messages"][-1], "tool_calls"):
            tool_calls = result["messages"][-1].tool_calls
            if tool_calls:
                console.print(f"[blue]Tool calls made: {len(tool_calls)}[/blue]")
                for i, call in enumerate(tool_calls):
                    console.print(f"  {i+1}. {call.get('name', 'Unknown tool')}")

        return result

    except Exception as e:
        console.print(f"[bold red]✗ Error in news analyst: {e}[/bold red]")
        raise

def test_fundamentals_analyst(
    ticker: str = "AAPL",
    trade_date: str = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Test the Fundamentals Analyst individually.

    Args:
        ticker: Stock ticker to analyze
        trade_date: Date for analysis
        config: Configuration to use

    Returns:
        Fundamentals analyst result state
    """
    console.print(Panel("[bold cyan]Testing Fundamentals Analyst[/bold cyan]", expand=False))

    # Create graph with only fundamentals analyst
    graph = create_debug_graph(["fundamentals"], config)
    initial_state = create_initial_state(ticker, trade_date)

    # Get the fundamentals analyst node
    fundamentals_node = graph.graph_setup.setup_graph(["fundamentals"]).nodes["fundamentals"]

    console.print(f"[yellow]Running fundamentals analysis for {ticker}...[/yellow]")

    try:
        result = fundamentals_node(initial_state)

        # Display results
        if result.get("fundamentals_report"):
            console.print(Panel(
                Markdown(result["fundamentals_report"]),
                title="Fundamentals Analysis Report",
                border_style="green"
            ))

        # Display tool calls if any
        if result.get("messages") and hasattr(result["messages"][-1], "tool_calls"):
            tool_calls = result["messages"][-1].tool_calls
            if tool_calls:
                console.print(f"[blue]Tool calls made: {len(tool_calls)}[/blue]")
                for i, call in enumerate(tool_calls):
                    console.print(f"  {i+1}. {call.get('name', 'Unknown tool')}")

        return result

    except Exception as e:
        console.print(f"[bold red]✗ Error in fundamentals analyst: {e}[/bold red]")
        raise

def test_all_analysts(
    ticker: str = "AAPL",
    trade_date: str = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Test all analysts sequentially and collect their reports.

    Args:
        ticker: Stock ticker to analyze
        trade_date: Date for analysis
        config: Configuration to use

    Returns:
        Combined results from all analysts
    """
    console.print(Panel("[bold magenta]Testing All Analysts[/bold magenta]", expand=False))

    analysts = ["market", "social", "news", "fundamentals"]
    results = {}

    for analyst in analysts:
        console.print(f"\n[bold blue]--- Testing {analyst.capitalize()} Analyst ---[/bold blue]")

        try:
            if analyst == "market":
                result = test_market_analyst(ticker, trade_date, config)
            elif analyst == "social":
                result = test_social_analyst(ticker, trade_date, config)
            elif analyst == "news":
                result = test_news_analyst(ticker, trade_date, config)
            elif analyst == "fundamentals":
                result = test_fundamentals_analyst(ticker, trade_date, config)

            results[analyst] = result
            console.print(f"[green]✓ {analyst.capitalize()} analyst completed[/green]")

        except Exception as e:
            console.print(f"[red]✗ {analyst.capitalize()} analyst failed: {e}[/red]")
            results[analyst] = {"error": str(e)}

    return results

# =============================================================================
# RESEARCH TEAM TESTING FUNCTIONS
# =============================================================================

def test_research_team_debate(
    ticker: str = "AAPL",
    trade_date: str = None,
    config: Optional[Dict[str, Any]] = None,
    analyst_reports: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Test the research team debate (Bull vs Bear researchers + Research Manager).

    Args:
        ticker: Stock ticker to analyze
        trade_date: Date for analysis
        config: Configuration to use
        analyst_reports: Pre-generated analyst reports (will generate if None)

    Returns:
        Research team debate results
    """
    console.print(Panel("[bold cyan]Testing Research Team Debate[/bold cyan]", expand=False))

    # Get analyst reports if not provided
    if analyst_reports is None:
        console.print("[yellow]Generating analyst reports first...[/yellow]")
        analyst_reports = test_all_analysts(ticker, trade_date, config)

    # Create full graph to test research team
    graph = create_debug_graph(["market", "social", "news", "fundamentals"], config)

    # Create state with analyst reports
    initial_state = create_initial_state(ticker, trade_date)

    # Add analyst reports to state
    for analyst, result in analyst_reports.items():
        if f"{analyst}_report" in result:
            initial_state[f"{analyst}_report"] = result[f"{analyst}_report"]

    console.print(f"[yellow]Running research team debate for {ticker}...[/yellow]")

    try:
        # Stream through the graph to get research team results
        args = graph.propagator.get_graph_args()

        research_results = None
        for chunk in graph.graph.stream(initial_state, **args):
            if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
                research_results = chunk
                break

        if research_results and "investment_debate_state" in research_results:
            debate_state = research_results["investment_debate_state"]

            # Display bull researcher analysis
            if debate_state.get("bull_history"):
                console.print(Panel(
                    Markdown(debate_state["bull_history"]),
                    title="Bull Researcher Analysis",
                    border_style="green"
                ))

            # Display bear researcher analysis
            if debate_state.get("bear_history"):
                console.print(Panel(
                    Markdown(debate_state["bear_history"]),
                    title="Bear Researcher Analysis",
                    border_style="red"
                ))

            # Display research manager decision
            if debate_state.get("judge_decision"):
                console.print(Panel(
                    Markdown(debate_state["judge_decision"]),
                    title="Research Manager Decision",
                    border_style="blue"
                ))

        return research_results or {}

    except Exception as e:
        console.print(f"[bold red]✗ Error in research team debate: {e}[/bold red]")
        raise

# =============================================================================
# TRADING TEAM TESTING FUNCTIONS
# =============================================================================

def test_trader(
    ticker: str = "AAPL",
    trade_date: str = None,
    config: Optional[Dict[str, Any]] = None,
    research_results: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Test the Trader agent.

    Args:
        ticker: Stock ticker to analyze
        trade_date: Date for analysis
        config: Configuration to use
        research_results: Pre-generated research results (will generate if None)

    Returns:
        Trader result state
    """
    console.print(Panel("[bold cyan]Testing Trader[/bold cyan]", expand=False))

    # Get research results if not provided
    if research_results is None:
        console.print("[yellow]Generating research results first...[/yellow]")
        analyst_reports = test_all_analysts(ticker, trade_date, config)
        research_results = test_research_team_debate(ticker, trade_date, config, analyst_reports)

    # Create full graph to test trader
    graph = create_debug_graph(["market", "social", "news", "fundamentals"], config)

    # Create state with research results
    initial_state = create_initial_state(ticker, trade_date)

    # Add research results to state
    if "investment_debate_state" in research_results:
        initial_state["investment_debate_state"] = research_results["investment_debate_state"]

    console.print(f"[yellow]Running trader analysis for {ticker}...[/yellow]")

    try:
        # Stream through the graph to get trader results
        args = graph.propagator.get_graph_args()

        trader_results = None
        for chunk in graph.graph.stream(initial_state, **args):
            if "trader_investment_plan" in chunk and chunk["trader_investment_plan"]:
                trader_results = chunk
                break

        if trader_results and "trader_investment_plan" in trader_results:
            console.print(Panel(
                Markdown(trader_results["trader_investment_plan"]),
                title="Trader Investment Plan",
                border_style="yellow"
            ))

        return trader_results or {}

    except Exception as e:
        console.print(f"[bold red]✗ Error in trader: {e}[/bold red]")
        raise

# =============================================================================
# RISK MANAGEMENT TESTING FUNCTIONS
# =============================================================================

def test_risk_management_team(
    ticker: str = "AAPL",
    trade_date: str = None,
    config: Optional[Dict[str, Any]] = None,
    trader_results: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Test the risk management team (Risky, Safe, Neutral analysts + Portfolio Manager).

    Args:
        ticker: Stock ticker to analyze
        trade_date: Date for analysis
        config: Configuration to use
        trader_results: Pre-generated trader results (will generate if None)

    Returns:
        Risk management team results
    """
    console.print(Panel("[bold cyan]Testing Risk Management Team[/bold cyan]", expand=False))

    # Get trader results if not provided
    if trader_results is None:
        console.print("[yellow]Generating trader results first...[/yellow]")
        analyst_reports = test_all_analysts(ticker, trade_date, config)
        research_results = test_research_team_debate(ticker, trade_date, config, analyst_reports)
        trader_results = test_trader(ticker, trade_date, config, research_results)

    # Create full graph to test risk management
    graph = create_debug_graph(["market", "social", "news", "fundamentals"], config)

    # Create state with trader results
    initial_state = create_initial_state(ticker, trade_date)

    # Add trader results to state
    if "trader_investment_plan" in trader_results:
        initial_state["trader_investment_plan"] = trader_results["trader_investment_plan"]

    console.print(f"[yellow]Running risk management analysis for {ticker}...[/yellow]")

    try:
        # Stream through the graph to get risk management results
        args = graph.propagator.get_graph_args()

        risk_results = None
        for chunk in graph.graph.stream(initial_state, **args):
            if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
                risk_results = chunk
                # Continue streaming to get final results

        if risk_results and "risk_debate_state" in risk_results:
            risk_state = risk_results["risk_debate_state"]

            # Display risky analyst analysis
            if risk_state.get("risky_history"):
                console.print(Panel(
                    Markdown(risk_state["risky_history"]),
                    title="Risky Analyst Analysis",
                    border_style="red"
                ))

            # Display safe analyst analysis
            if risk_state.get("safe_history"):
                console.print(Panel(
                    Markdown(risk_state["safe_history"]),
                    title="Safe Analyst Analysis",
                    border_style="green"
                ))

            # Display neutral analyst analysis
            if risk_state.get("neutral_history"):
                console.print(Panel(
                    Markdown(risk_state["neutral_history"]),
                    title="Neutral Analyst Analysis",
                    border_style="yellow"
                ))

            # Display portfolio manager decision
            if risk_state.get("judge_decision"):
                console.print(Panel(
                    Markdown(risk_state["judge_decision"]),
                    title="Portfolio Manager Final Decision",
                    border_style="blue"
                ))

        return risk_results or {}

    except Exception as e:
        console.print(f"[bold red]✗ Error in risk management team: {e}[/bold red]")
        raise

# =============================================================================
# FULL WORKFLOW TESTING FUNCTIONS
# =============================================================================

def test_full_workflow(
    ticker: str = "AAPL",
    trade_date: str = None,
    config: Optional[Dict[str, Any]] = None,
    analysts: List[str] = ["market", "social", "news", "fundamentals"]
) -> Dict[str, Any]:
    """
    Test the complete TradingAgents workflow from start to finish.

    Args:
        ticker: Stock ticker to analyze
        trade_date: Date for analysis
        config: Configuration to use
        analysts: List of analysts to include

    Returns:
        Final workflow results
    """
    console.print(Panel("[bold magenta]Testing Full Workflow[/bold magenta]", expand=False))

    # Create graph with selected analysts
    graph = create_debug_graph(analysts, config)
    initial_state = create_initial_state(ticker, trade_date)

    console.print(f"[yellow]Running full workflow for {ticker} on {trade_date}...[/yellow]")

    try:
        # Run the complete workflow
        args = graph.propagator.get_graph_args()

        # Stream through the entire workflow
        trace = []
        for chunk in graph.graph.stream(initial_state, **args):
            trace.append(chunk)

            # Print progress updates
            if "market_report" in chunk and chunk["market_report"]:
                console.print("[green]✓ Market analysis completed[/green]")
            if "sentiment_report" in chunk and chunk["sentiment_report"]:
                console.print("[green]✓ Social sentiment analysis completed[/green]")
            if "news_report" in chunk and chunk["news_report"]:
                console.print("[green]✓ News analysis completed[/green]")
            if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
                console.print("[green]✓ Fundamentals analysis completed[/green]")
            if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
                console.print("[green]✓ Research team debate completed[/green]")
            if "trader_investment_plan" in chunk and chunk["trader_investment_plan"]:
                console.print("[green]✓ Trading plan completed[/green]")
            if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
                console.print("[green]✓ Risk management analysis completed[/green]")

        # Get final state
        final_state = trace[-1] if trace else {}

        # Process final decision
        if "final_trade_decision" in final_state:
            decision = graph.process_signal(final_state["final_trade_decision"])
            console.print(Panel(
                f"[bold green]Final Trading Decision: {decision}[/bold green]",
                title="Workflow Complete",
                border_style="green"
            ))

        return final_state

    except Exception as e:
        console.print(f"[bold red]✗ Error in full workflow: {e}[/bold red]")
        raise

def test_streaming_analysis(
    ticker: str = "AAPL",
    trade_date: str = None,
    config: Optional[Dict[str, Any]] = None,
    analysts: List[str] = ["market"]
) -> List[Dict[str, Any]]:
    """
    Test the streaming analysis with detailed step-by-step output.

    Args:
        ticker: Stock ticker to analyze
        trade_date: Date for analysis
        config: Configuration to use
        analysts: List of analysts to include

    Returns:
        List of all streaming chunks
    """
    console.print(Panel("[bold cyan]Testing Streaming Analysis[/bold cyan]", expand=False))

    # Create graph with selected analysts
    graph = create_debug_graph(analysts, config)
    initial_state = create_initial_state(ticker, trade_date)

    console.print(f"[yellow]Starting streaming analysis for {ticker}...[/yellow]")

    try:
        args = graph.propagator.get_graph_args()

        trace = []
        step = 1

        for chunk in graph.graph.stream(initial_state, **args):
            trace.append(chunk)

            console.print(f"\n[bold blue]--- Step {step} ---[/bold blue]")

            # Display messages if any
            if "messages" in chunk and chunk["messages"]:
                last_message = chunk["messages"][-1]
                if hasattr(last_message, "content"):
                    content = last_message.content
                    if isinstance(content, list):
                        # Handle Anthropic format
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                text_parts.append(item.get('text', ''))
                        content = ' '.join(text_parts)

                    if content and len(content) > 200:
                        content = content[:200] + "..."

                    console.print(f"[dim]Message: {content}[/dim]")

                # Display tool calls
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    console.print(f"[blue]Tool calls: {len(last_message.tool_calls)}[/blue]")
                    for i, call in enumerate(last_message.tool_calls):
                        tool_name = call.get('name', 'Unknown') if isinstance(call, dict) else getattr(call, 'name', 'Unknown')
                        console.print(f"  {i+1}. {tool_name}")

            # Display state updates
            state_updates = []
            for key in ["market_report", "sentiment_report", "news_report", "fundamentals_report",
                       "trader_investment_plan", "final_trade_decision"]:
                if key in chunk and chunk[key]:
                    state_updates.append(key.replace("_", " ").title())

            if state_updates:
                console.print(f"[green]State updates: {', '.join(state_updates)}[/green]")

            step += 1

        console.print(f"\n[bold green]Streaming analysis completed in {step-1} steps[/bold green]")
        return trace

    except Exception as e:
        console.print(f"[bold red]✗ Error in streaming analysis: {e}[/bold red]")
        raise

# =============================================================================
# STATE INSPECTION UTILITIES
# =============================================================================

def inspect_state(state: Dict[str, Any], title: str = "State Inspection"):
    """
    Display detailed information about a state object.

    Args:
        state: State dictionary to inspect
        title: Title for the inspection panel
    """
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]", expand=False))

    # Create table for state information
    table = Table(title="State Contents", box=box.ROUNDED)
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Type", style="yellow", no_wrap=True)
    table.add_column("Value/Length", style="green")

    for key, value in state.items():
        if isinstance(value, str):
            display_value = value[:100] + "..." if len(value) > 100 else value
            table.add_row(key, "str", display_value)
        elif isinstance(value, list):
            table.add_row(key, "list", f"Length: {len(value)}")
        elif isinstance(value, dict):
            table.add_row(key, "dict", f"Keys: {len(value)}")
        else:
            table.add_row(key, type(value).__name__, str(value)[:50])

    console.print(table)

def save_state_to_file(state: Dict[str, Any], filename: str = None):
    """
    Save state to a JSON file for later inspection.

    Args:
        state: State dictionary to save
        filename: Output filename (auto-generated if None)
    """
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"debug_state_{timestamp}.json"

    # Convert state to JSON-serializable format
    json_state = {}
    for key, value in state.items():
        if isinstance(value, (str, int, float, bool, list, dict)):
            json_state[key] = value
        else:
            json_state[key] = str(value)

    try:
        with open(filename, 'w') as f:
            json.dump(json_state, f, indent=2)
        console.print(f"[green]State saved to {filename}[/green]")
    except Exception as e:
        console.print(f"[red]Error saving state: {e}[/red]")

def compare_states(state1: Dict[str, Any], state2: Dict[str, Any]):
    """
    Compare two states and show differences.

    Args:
        state1: First state to compare
        state2: Second state to compare
    """
    console.print(Panel("[bold cyan]State Comparison[/bold cyan]", expand=False))

    all_keys = set(state1.keys()) | set(state2.keys())

    table = Table(title="State Differences", box=box.ROUNDED)
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("State 1", style="green")
    table.add_column("State 2", style="yellow")
    table.add_column("Status", style="red")

    for key in sorted(all_keys):
        val1 = state1.get(key, "[missing]")
        val2 = state2.get(key, "[missing]")

        if key not in state1:
            status = "Added"
        elif key not in state2:
            status = "Removed"
        elif val1 != val2:
            status = "Changed"
        else:
            status = "Same"
            continue  # Skip unchanged items

        # Truncate long values
        if isinstance(val1, str) and len(val1) > 50:
            val1 = val1[:50] + "..."
        if isinstance(val2, str) and len(val2) > 50:
            val2 = val2[:50] + "..."

        table.add_row(key, str(val1), str(val2), status)

    console.print(table)

# =============================================================================
# MAIN TESTING FUNCTIONS
# =============================================================================

def run_debug_menu():
    """
    Interactive debug menu for testing different components.
    """
    console.print(Panel(
        "[bold green]TradingAgents Debug Menu[/bold green]\n"
        "Choose what you want to test:",
        title="Debug Menu",
        border_style="green"
    ))

    options = [
        "1. Test individual Market Analyst",
        "2. Test individual Social Analyst",
        "3. Test individual News Analyst",
        "4. Test individual Fundamentals Analyst",
        "5. Test all Analysts",
        "6. Test Research Team Debate",
        "7. Test Trader",
        "8. Test Risk Management Team",
        "9. Test Full Workflow",
        "10. Test Streaming Analysis",
        "11. Custom Configuration Test",
        "0. Exit"
    ]

    for option in options:
        console.print(option)

    choice = input("\nEnter your choice (0-11): ").strip()

    # Get common parameters
    ticker = input("Enter ticker symbol (default: AAPL): ").strip() or "AAPL"
    trade_date = input("Enter trade date YYYY-MM-DD (default: yesterday): ").strip()
    if not trade_date:
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        trade_date = yesterday.strftime("%Y-%m-%d")

    # Create default config
    config = create_debug_config()

    try:
        if choice == "1":
            test_market_analyst(ticker, trade_date, config)
        elif choice == "2":
            test_social_analyst(ticker, trade_date, config)
        elif choice == "3":
            test_news_analyst(ticker, trade_date, config)
        elif choice == "4":
            test_fundamentals_analyst(ticker, trade_date, config)
        elif choice == "5":
            test_all_analysts(ticker, trade_date, config)
        elif choice == "6":
            test_research_team_debate(ticker, trade_date, config)
        elif choice == "7":
            test_trader(ticker, trade_date, config)
        elif choice == "8":
            test_risk_management_team(ticker, trade_date, config)
        elif choice == "9":
            test_full_workflow(ticker, trade_date, config)
        elif choice == "10":
            test_streaming_analysis(ticker, trade_date, config)
        elif choice == "11":
            # Custom configuration
            console.print("[yellow]Custom configuration not implemented in menu[/yellow]")
        elif choice == "0":
            console.print("[green]Goodbye![/green]")
            return
        else:
            console.print("[red]Invalid choice[/red]")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

# =============================================================================
# EXAMPLE USAGE AND MAIN FUNCTION
# =============================================================================

if __name__ == '__main__':
    """
    Main function with example usage.

    Uncomment the sections you want to test:
    """

    # Example 1: Test individual market analyst
    # console.print("[bold blue]Example 1: Testing Market Analyst[/bold blue]")
    # config = create_debug_config(online_tools=False)  # Use cached data for faster testing
    # result = test_market_analyst("AAPL", "2024-01-15", config)

    # Example 2: Test all analysts
    # console.print("[bold blue]Example 2: Testing All Analysts[/bold blue]")
    # config = create_debug_config()
    # results = test_all_analysts("NVDA", "2024-01-15", config)

    # Example 3: Test full workflow with minimal config
    # console.print("[bold blue]Example 3: Testing Full Workflow[/bold blue]")
    # config = create_debug_config(
    #     deep_model="gpt-4o-mini",
    #     quick_model="gpt-4o-mini",
    #     max_debate_rounds=1,
    #     online_tools=True
    # )
    # final_state = test_full_workflow("TSLA", "2024-01-15", config, ["market"])

    # Example 4: Test streaming analysis
    # console.print("[bold blue]Example 4: Testing Streaming Analysis[/bold blue]")
    # config = create_debug_config()
    # trace = test_streaming_analysis("AAPL", "2024-01-15", config, ["market"])

    # Interactive menu (uncomment to use)
    run_debug_menu()