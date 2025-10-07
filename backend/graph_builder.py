from langgraph.graph import StateGraph, START, END
from typing import TypedDict

from agents.data_extraction_agent import DataExtractionAgent
from agents.finance_agent import FinanceAgent
from agents.math_agent import MathAgent
from agents.market_agent import MarketAgent
from agents.sentiment_agent import SentimentAgent
from agents.supervisor_agent import SupervisorAgent

class FinanceState(TypedDict):
    file_path: str
    financials: dict
    ratios: dict
    market_data: dict
    sentiment: dict
    markdown_file: str
    executive_summary: str

def data_extraction_node(state: FinanceState):
    extracted = DataExtractionAgent().extract(state['file_path'])
    return {"financials": extracted}

def ratio_calc_node(state: FinanceState):
    ratios = MathAgent().compute_ratios(state['financials'])
    return {"ratios": ratios}

def market_node(state: FinanceState):
    financials = state.get("financials", {})
    symbol = financials.get("symbol")
    company_name = financials.get("company_name")
    market = MarketAgent().fetch(symbol=symbol, company_name=company_name)
    return {"market_data": market}

def sentiment_node(state: FinanceState):
    financials = state.get("financials", {})
    symbol = financials.get("symbol")
    company_name = financials.get("company_name")
    sentiment = SentimentAgent().analyze(symbol=symbol, company_name=company_name)
    return {"sentiment": sentiment}

def supervisor_node(state: FinanceState):
    # Aggregate, LLM summary, and markdown writing handled by supervisor agent
    result = SupervisorAgent().aggregate_and_write(state)
    return {
        "markdown_file": result["markdown_file"],
        "executive_summary": result["executive_summary"]
    }

def build_graph():
    builder = StateGraph(FinanceState)
    builder.add_node("data_extraction", data_extraction_node)
    builder.add_node("ratio_calc", ratio_calc_node)
    builder.add_node("market", market_node)
    builder.add_node("sentiment", sentiment_node)
    builder.add_node("supervisor", supervisor_node)

    builder.add_edge(START, "data_extraction")
    builder.add_edge("data_extraction", "ratio_calc")
    builder.add_edge("data_extraction", "market")
    builder.add_edge("data_extraction", "sentiment")
    builder.add_edge("ratio_calc", "supervisor")
    builder.add_edge("market", "supervisor")
    builder.add_edge("sentiment", "supervisor")
    builder.add_edge("supervisor", END)
    
    graph=builder.compile()
    return graph


if __name__ == "__main__":
    workflow = build_graph()
    

    state = {"file_path": "W:/anaconda/Financial_report_analyzer/backend/input/FY25_Q3_Consolidated_Financial_Statements.pdf"}
    result = workflow.invoke(state)
    print("Markdown report saved at:", result["markdown_file"])
    print("Executive Summary:\n", result["executive_summary"])
