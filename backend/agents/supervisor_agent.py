from ..utils.output_write import write_markdown
from ..utils.llm_starter import summarize  # Assume this calls OpenAI or other LLM

class SupervisorAgent:
    def __init__(self):
        pass  # No agent composition needed for parallel graph execution

    def aggregate_and_write(self, state: dict):
        # Retrieve outputs from state dict
        financials = state.get("financials", {})
        ratios = state.get("ratios", {})
        market_data = state.get("market_data", {})
        sentiment = state.get("sentiment", {})

        # Compose executive summary using LLM
        summary_prompt = (
            f"Write an executive summary of the following financial analysis:\n\n"
            f"Key financials: {financials}\n"
            f"Ratios: {ratios}\n"
            f"Market Data: {market_data}\n"
            f"Sentiment Analysis: {sentiment}\n"
        )
        exec_summary = summarize(summary_prompt)

        # Prepare the full result dictionary, including LLM-generated summary
        result = {
            "financials": financials,
            "ratios": ratios,
            "market_data": market_data,
            "sentiment": sentiment,
            "executive_summary": exec_summary
        }

        symbol = financials.get("symbol") or "report"
        md_file = write_markdown(result, symbol)
        result["markdown_file"] = md_file
        return result
