import os

def write_markdown(result, symbol=None):
    output_dir = "W:/anaconda/Financial_report_analyzer/backend/output"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{symbol or 'report'}_analysis.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Financial Analysis Report for {symbol or 'Company'}\n\n")
        if "executive_summary" in result:
            f.write("## Executive Summary\n")
            f.write(result["executive_summary"] + "\n\n")
        # Financials
        f.write("## Financials\n")
        for key, value in result.get("financials", {}).items():
            f.write(f"- **{key.replace('_', ' ').title()}**: {value}\n")
        f.write("\n")
        # Ratios
        f.write("## Ratios\n")
        for key, value in result.get("ratios", {}).items():
            f.write(f"- **{key.replace('_', ' ').title()}**: {value}\n")
        f.write("\n")
        # Market Data
        f.write("## Market Data\n")
        market_data = result.get("market_data", {})
        if market_data:
            for key, value in market_data.items():
                f.write(f"- **{key.replace('_', ' ').title()}**: {value}\n")
        else:
            f.write("No market data available.\n")
        f.write("\n")
        # Sentiment as tables
        f.write("## Sentiment Analysis\n")
        sentiment = result.get("sentiment", {})
        if sentiment and sentiment.get("total_articles", 0) > 0:
            f.write(f"- **Total Articles Analyzed**: {sentiment['total_articles']}\n")
            f.write(f"- **Confidence Score**: {sentiment.get('confidence_score', 0)}\n\n")
            # Summary Table
            f.write("| Sentiment | Count | Percent | Sample Headlines |\n")
            f.write("|-----------|-------|---------|-----------------|\n")
            for sent in ("positive", "negative", "neutral"):
                count = sentiment.get(sent, 0)
                pct = sentiment.get("sentiment_breakdown", {}).get(f"{sent}_pct", 0)
                samples = sentiment.get("sample_headlines", {}).get(sent, [])
                sample_md = "<br>".join(samples) if samples else "-"
                f.write(f"| {sent.title()} | {count} | {pct}% | {sample_md} |\n")
            f.write("\n")
            # Top Headlines Table
            f.write("### Top Headlines (first 10)\n")
            f.write("| Sentiment | Score | Headline |\n")
            f.write("|-----------|-------|----------|\n")
            for hd in sentiment.get("headlines", [])[:10]:
                sclass = hd.get("sentiment", "-").title()
                score = hd.get("score", 0)
                title = hd.get("title", "")
                url = hd.get("url", "")
                title_md = f"[{title}]({url})" if url else title
                f.write(f"| {sclass} | {score:+.2f} | {title_md} |\n")
            if len(sentiment.get("headlines", [])) > 10:
                # f.write(f"| ...{len(sentiment['headlines'])-10} more... |||\n")
                pass
            f.write("\n")
        else:
            f.write("No sentiment data available.\n")
        f.write("\n")
    return filepath
