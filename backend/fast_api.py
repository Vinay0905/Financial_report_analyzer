from fastapi import FastAPI, UploadFile, File
from graph_builder import build_graph

app = FastAPI()
workflow = build_graph()

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

# Run with: uvicorn fast_api:app --reload
