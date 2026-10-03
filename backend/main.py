import os
import json
import io
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from models import Persona, SimulateAARequest, IngestionResponse
from services.aggregator import process_and_aggregate_transactions

app = FastAPI(
    title="AltCredit - Ingestion & Aggregation Service",
    description="API for alternative financial transaction parsing, PII sanitization, and solvency metrics.",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@app.get("/")
def health_check():
    return {"status": "online", "service": "AltCredit Ingestion Engine", "docs": "/docs"}

@app.get("/api/v1/personas", response_model=List[Persona])
def get_personas():
    personas_path = os.path.join(DATA_DIR, "personas.json")
    if not os.path.exists(personas_path):
        raise HTTPException(status_code=404, detail="Personas not found.")
    with open(personas_path, "r") as f:
        return json.load(f)

@app.post("/api/v1/ingest/simulate-aa", response_model=IngestionResponse)
def simulate_account_aggregator(req: SimulateAARequest):
    csv_file = f"{req.persona_id}.csv"
    file_path = os.path.join(DATA_DIR, csv_file)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Persona dataset '{csv_file}' not found.")

    personas_path = os.path.join(DATA_DIR, "personas.json")
    persona_name = "Anonymous Applicant"
    if os.path.exists(personas_path):
        with open(personas_path, "r") as f:
            for p in json.load(f):
                if p["id"] == req.persona_id:
                    persona_name = f"{p['name']} ({p['title']})"
                    break

    df = pd.read_csv(file_path)
    applicant_id = f"ALT-{abs(hash(req.persona_id)) % 10000:04d}"
    return process_and_aggregate_transactions(df, applicant_id, persona_name)

@app.post("/api/v1/ingest/upload", response_model=IngestionResponse)
async def upload_statement(file: UploadFile = File(...)):
    if not (file.filename.endswith(".csv") or file.filename.endswith(".json")):
        raise HTTPException(status_code=400, detail="Only .csv and .json statements are supported.")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content)) if file.filename.endswith(".csv") else pd.DataFrame(json.loads(content.decode("utf-8")))
        return process_and_aggregate_transactions(df, f"ALT-UPLOAD-{file.filename[:5].upper()}", "Uploaded Statement")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)