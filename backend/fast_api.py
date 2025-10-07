from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from .graph.graph_builder import build_graph
from .agents.supervisor_agent import SupervisorAgent

app = FastAPI()
workflow = build_graph()

class SupervisorInput(BaseModel):
    financials: dict
    ratios: dict
    market_data: dict
    sentiment: dict

@app.post("/analyze/")
async def analyze_report(file: UploadFile = File(...)):
    file_path = f"./tmp/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    result = workflow.invoke({"file_path": file_path})
    return {
        "markdown_file": result["markdown_file"],
        "executive_summary": result.get("executive_summary", "")
    }

@app.post("/supervisor/")
async def supervisor_endpoint(data: SupervisorInput):
    agent = SupervisorAgent()
    result = agent.aggregate_and_write(data.dict())
    return result

# Run with: uvicorn fast_api:app --reload
