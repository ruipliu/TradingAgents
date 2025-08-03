import time
import json


def create_comprehensive_decision_agent(llm, unified_memory):
    """
    Create a comprehensive decision agent that combines the functionality of:
    - Bull/Bear research and debate
    - Investment decision making
    - Trading plan creation
    - Risk analysis from multiple perspectives
    - Final trading decision
    """
    def comprehensive_decision_node(state) -> dict:
        company_name = state["company_of_interest"]
        trade_date = state["trade_date"]

        # Get all analyst reports
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # Combine all reports for memory lookup
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"

        # Get memories from unified memory (includes all past experiences)
        past_memories = unified_memory.get_memories(curr_situation, n_matches=5)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += f"Memory {i}: {rec['recommendation']}\n\n"
        else:
            past_memory_str = "No past memories found."

        prompt = f"""You are a comprehensive trading decision agent responsible for analyzing all available information and making a final trading decision for {company_name} on {trade_date}.

Your task is to:
1. Analyze the situation from both BULLISH and BEARISH perspectives
2. Consider AGGRESSIVE, NEUTRAL, and CONSERVATIVE risk approaches
3. Create a detailed investment plan
4. Make a final trading decision (BUY, SELL, or HOLD)

AVAILABLE INFORMATION:
===================

Market Research Report:
{market_research_report}

Social Media Sentiment Report:
{sentiment_report}

Latest News Report:
{news_report}

Company Fundamentals Report:
{fundamentals_report}

Past Lessons and Reflections:
{past_memory_str}

ANALYSIS FRAMEWORK:
==================

1. BULLISH PERSPECTIVE ANALYSIS:
   - Identify all positive factors from the reports
   - Consider growth opportunities, positive sentiment, favorable market conditions
   - Evaluate potential upside scenarios
   - Address any bearish concerns with counter-arguments

2. BEARISH PERSPECTIVE ANALYSIS:
   - Identify all risk factors and negative indicators
   - Consider market headwinds, negative sentiment, fundamental weaknesses
   - Evaluate potential downside scenarios
   - Challenge bullish assumptions with realistic concerns

3. RISK ASSESSMENT:
   - AGGRESSIVE APPROACH: Focus on high-reward opportunities, accept higher volatility
   - CONSERVATIVE APPROACH: Prioritize capital preservation, minimize downside risk
   - BALANCED APPROACH: Weigh risk-reward ratios, consider diversification

4. INVESTMENT DECISION SYNTHESIS:
   - Weigh all perspectives and risk considerations
   - Learn from past mistakes reflected in memories
   - Create a comprehensive investment plan
   - Make a decisive recommendation with clear rationale

DELIVERABLES:
============

Provide your analysis in the following structure:

**BULLISH ANALYSIS:**
[Your bullish perspective analysis]

**BEARISH ANALYSIS:**
[Your bearish perspective analysis]

**RISK ASSESSMENT:**
- Aggressive perspective: [analysis]
- Conservative perspective: [analysis]
- Balanced perspective: [analysis]

**INVESTMENT PLAN:**
[Detailed investment strategy and rationale]

**FINAL DECISION:**
Based on comprehensive analysis, my recommendation is: **BUY/SELL/HOLD**

**RATIONALE:**
[Clear explanation of why this decision was made, addressing key factors and lessons learned]

Remember to:
- Be decisive and avoid defaulting to HOLD without strong justification
- Use real data instead of hallucinating
- Learn from past mistakes mentioned in the memories
- Consider all perspectives but make a clear final choice
- Provide actionable insights for implementation
"""

        response = llm.invoke(prompt)

        # Parse the response to extract different sections
        content = response.content

        # Extract investment plan (comprehensive analysis)
        investment_plan = content

        # Extract trading plan section
        trader_plan_start = content.find("**INVESTMENT PLAN:**")
        trader_plan_end = content.find("**FINAL DECISION:**")
        if trader_plan_start != -1 and trader_plan_end != -1:
            trader_investment_plan = content[trader_plan_start:trader_plan_end].strip()
        else:
            # Fallback: use the full content if sections not found
            trader_investment_plan = content

        # Extract final decision section
        final_decision_start = content.find("**FINAL DECISION:**")
        if final_decision_start != -1:
            final_trade_decision = content[final_decision_start:].strip()
        else:
            # Fallback: use the full content if section not found
            final_trade_decision = content

        # Update state with distinct content for each section
        return {
            "investment_plan": investment_plan,
            "trader_investment_plan": trader_investment_plan,
            "final_trade_decision": final_trade_decision,
            "messages": [response],
            "sender": "Comprehensive Decision Agent"
        }
    
    return comprehensive_decision_node
