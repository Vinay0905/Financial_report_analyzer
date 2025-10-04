# Multi-Agent Financial Report Analyzer with LangGraph

A production-ready, agentic AI system using LangGraph to automate comprehensive financial report analysis for companies.

## Features
- Data Extraction Agent for parsing structured and unstructured report data
- Finance Agent for extracting key financial metrics and computing ratios
- Math Agent for quantitative analysis and anomaly detection
- Market Agent for integrating external market data
- Sentiment Agent for analyzing qualitative signals
- Supervisor Agent for orchestrating workflow and delivering narrative summaries

## Architecture
The system uses LangGraph to coordinate a team of specialized agents, each responsible for a unique analytical task. Results are delivered through a secure web frontend as actionable reports.

## Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`

## Usage
Run the application: `python backend/main.py`


financial_report_analyzer/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── data_extraction_agent.py
│   │   ├── finance_agent.py
│   │   ├── math_agent.py
│   │   ├── market_agent.py
│   │   ├── sentiment_agent.py
│   │   └── supervisor_agent.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── document_parser.py
│   │   ├── financial_calculations.py
│   │   ├──data_visualization.py
        └── llm_starter.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── main.py
    ├── fast_api.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── styles/
│   │   └── main.css
│   ├── js/
│   │   ├── app.js
│   │   └── api.js
│   └── assets/
├── data/
│   ├── input/
│   ├── output/
│   └── cache/
├── tests/
│   ├── test_agents/
│   └── test_utils/
├── README.md
└── requirements.txt
