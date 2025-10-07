from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
# Add this import
from fastapi.middleware.cors import CORSMiddleware


from .graph.graph_builder import build_graph
from .agents.supervisor_agent import SupervisorAgent
import os

# from .graph.graph_builder import build_graph  # Assuming this exists
# from .agents.supervisor_agent import SupervisorAgent # Assuming this exists

app = FastAPI()

# Add these lines to configure CORS
origins = [
    # Add the URL of your frontend app.
    # If you are running it locally, it might be one of these.
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173", # Common for Vite
    # Add the URL of your deployed project here
]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
workflow = build_graph()
INPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "input"))
OUTPUT_FOLDER=os.path.abspath(os.path.join(os.path.dirname(__file__), "output"))

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
last_report_filepath: Optional[str] = None

class SupervisorInput(BaseModel):
    financials: dict
    ratios: dict
    market_data: dict
    sentiment: dict

    



@app.post("/analyze/", status_code=status.HTTP_200_OK)
async def analyze_report(file: UploadFile = File(...)):
    """
    Uploads a financial PDF file, saves to the input folder,
    and runs the analysis workflow. Remembers the report filepath for download.
    """
    global last_report_filepath
    try:
        # Clean the filename to avoid path traversal
        filename = os.path.basename(file.filename)
        file_path = os.path.join(INPUT_FOLDER, filename)

        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Run workflow
        result = workflow.invoke({"file_path": file_path})

        # Remember the markdown report filepath for download
        last_report_filepath = result.get("markdown_file")

        return {
            "markdown_file": last_report_filepath,
            "executive_summary": result.get("executive_summary", "")
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@app.post("/supervisor/", status_code=status.HTTP_200_OK)
async def supervisor_endpoint(data: SupervisorInput):
    """
    Runs the supervisor agent aggregation and markdown writing.
    """
    try:
        agent = SupervisorAgent()
        result = agent.aggregate_and_write(data.dict())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Supervisor error: {str(e)}"
        )
@app.get("/download_last_report/", response_class=FileResponse)
async def download_last_report():
    """
    Download the most recent markdown report file created during analysis.
    """
    global last_report_filepath
    if not last_report_filepath or not os.path.isfile(last_report_filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found. Please run analysis first."
        )

    return FileResponse(
        path=last_report_filepath,
        media_type='text/markdown',
        filename=os.path.basename(last_report_filepath)
    )


# Run with: uvicorn fast_api2:app --reload