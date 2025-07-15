# TradingAgents Debug Guide

This guide explains how to use the debug functions to test individual components of the TradingAgentsGraph.

## Quick Start

1. **Run the interactive debug menu:**
   ```bash
   python debug.py
   ```

2. **Run specific examples:**
   ```bash
   python debug_examples.py
   ```

## Available Debug Functions

### Configuration Functions

- `create_debug_config()` - Create custom configuration for testing
- `print_config_info()` - Display configuration in a nice table format

### Individual Agent Testing

- `test_market_analyst()` - Test market data analysis
- `test_social_analyst()` - Test social sentiment analysis  
- `test_news_analyst()` - Test news analysis
- `test_fundamentals_analyst()` - Test fundamental analysis
- `test_all_analysts()` - Test all analysts sequentially

### Team Testing Functions

- `test_research_team_debate()` - Test bull vs bear researcher debate
- `test_trader()` - Test trading plan generation
- `test_risk_management_team()` - Test risk analysis team

### Workflow Testing

- `test_full_workflow()` - Test complete end-to-end workflow
- `test_streaming_analysis()` - Test with detailed step-by-step output

### State Inspection Utilities

- `inspect_state()` - Display detailed state information
- `save_state_to_file()` - Save state to JSON file
- `compare_states()` - Compare two states and show differences

## Configuration Options

### LLM Providers
- `openai` - OpenAI GPT models
- `anthropic` - Anthropic Claude models  
- `google` - Google Gemini models
- `ollama` - Local Ollama models
- `openrouter` - OpenRouter API

### Common Models
- OpenAI: `gpt-4o-mini`, `gpt-4o`, `o1-mini`, `o1`
- Anthropic: `claude-3-haiku-20240307`, `claude-3-sonnet-20240229`
- Google: `gemini-2.0-flash`, `gemini-1.5-pro`

## Example Usage

### Test Single Analyst
```python
from debug import *

# Create configuration
config = create_debug_config(
    llm_provider="openai",
    deep_model="gpt-4o-mini",
    quick_model="gpt-4o-mini",
    online_tools=True
)

# Test market analyst
result = test_market_analyst("AAPL", "2024-01-15", config)
```

### Test Full Workflow
```python
# Minimal config for testing
config = create_debug_config(
    max_debate_rounds=1,
    max_risk_rounds=1,
    online_tools=False  # Use cached data
)

# Test with selected analysts
final_state = test_full_workflow(
    ticker="AAPL",
    trade_date="2024-01-15", 
    config=config,
    analysts=["market", "news"]  # Just these analysts
)
```

### Custom Configuration Testing
```python
# Test different LLM providers
configs = [
    create_debug_config(llm_provider="openai", deep_model="gpt-4o-mini"),
    create_debug_config(llm_provider="anthropic", deep_model="claude-3-haiku-20240307")
]

for config in configs:
    result = test_market_analyst("AAPL", "2024-01-15", config)
```

## Input Parameters You Need to Provide

When using the debug functions, you'll typically need to specify:

1. **ticker** (string): Stock symbol to analyze (e.g., "AAPL", "NVDA", "TSLA")
2. **trade_date** (string): Date in YYYY-MM-DD format (use past dates to avoid future date errors)
3. **config** (dict): Configuration dictionary (optional, uses defaults if not provided)
4. **analysts** (list): Which analysts to include (["market", "social", "news", "fundamentals"])

## Common Testing Scenarios

### 1. Quick Single Agent Test
```python
from debug import *

# Test just market analyst with minimal config
config = create_debug_config(online_tools=False)
result = test_market_analyst("AAPL", "2024-01-15", config)
```

### 2. Full Pipeline Test
```python
from debug import *

# Test complete workflow with all agents
config = create_debug_config(max_debate_rounds=1)
final_state = test_full_workflow("AAPL", "2024-01-15", config)
```

### 3. Streaming Debug
```python
from debug import *

# Watch step-by-step execution
config = create_debug_config()
trace = test_streaming_analysis("AAPL", "2024-01-15", config, ["market"])
```

### 4. State Inspection
```python
# Examine intermediate states
initial_state = create_initial_state("AAPL", "2024-01-15")
inspect_state(initial_state)
```

## Tips for Debugging

1. **Start Small**: Begin with single analyst tests before full workflow
2. **Use Cached Data**: Set `online_tools=False` for faster testing
3. **Reduce Debate Rounds**: Set `max_debate_rounds=1` for quicker results
4. **Use Cheaper Models**: Use `gpt-4o-mini` instead of `gpt-4o` for testing
5. **Save States**: Use `save_state_to_file()` to examine results later
6. **Check Past Dates**: Always use past dates to avoid "future date" errors

## Troubleshooting

### Common Issues:
- **Future Date Error**: Use dates in the past (e.g., "2024-01-15")
- **API Key Issues**: Make sure your API keys are set in environment variables
- **Model Not Found**: Check if the model name is correct for your provider
- **Tool Errors**: Try setting `online_tools=False` to use cached data

### Error Debugging:
- Use `inspect_state()` to examine state at different points
- Check the streaming output with `test_streaming_analysis()`
- Save intermediate states with `save_state_to_file()`
- Compare states before/after operations with `compare_states()`

## Interactive Menu

Run `python cli/debug.py` for an interactive menu with these options:
1. Test individual Market Analyst
2. Test individual Social Analyst
3. Test individual News Analyst
4. Test individual Fundamentals Analyst
5. Test all Analysts
6. Test Research Team Debate
7. Test Trader
8. Test Risk Management Team
9. Test Full Workflow
10. Test Streaming Analysis
11. Custom Configuration Test

The menu will prompt you for ticker symbol and date, then run the selected test.
