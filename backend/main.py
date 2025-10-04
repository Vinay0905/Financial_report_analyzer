from graph_builder import build_graph

def analyze_file(filepath):
    workflow = build_graph()
    state = {"file_path": filepath}
    result = workflow.invoke(state)
    print(f"Markdown report: {result['markdown_file']}")
    print("\nExecutive Summary:\n", result.get("executive_summary", ""))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Analyze a financial report via LangGraph agents.")
    parser.add_argument("filepath", type=str, help="Path to input report file")
    args = parser.parse_args()
    analyze_file(args.filepath)
