from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .dataset_loader import list_change_presets, list_dataset_options, load_dataset_by_id
from .engine.analyze import analyze_model
from .schema import (
    AnalyzeAcceptedResponse,
    AnalyzeRequest,
    DatasetsResponse,
    JobRequestEcho,
    JobResponse,
    PresetsResponse,
)
from .store import job_store


app = FastAPI(title="Cross Discipline Impact Analyzer API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze", response_model=AnalyzeAcceptedResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeAcceptedResponse:
    if request.datasetId is not None:
        resolved_model = load_dataset_by_id(request.datasetId)
        dataset_id = request.datasetId
    else:
        resolved_model = request.datasetJson
        dataset_id = "inline"

    if resolved_model is None:
        raise HTTPException(status_code=400, detail="Unable to resolve dataset")

    resolved_ids = {element.id for element in resolved_model.elements}
    unknown_ids = [element_id for element_id in request.changeEvent.elementIds if element_id not in resolved_ids]
    if unknown_ids:
        raise HTTPException(status_code=400, detail=f"Unknown change elementIds: {unknown_ids}")

    job = job_store.create(
        JobRequestEcho(datasetId=dataset_id, resolvedModel=resolved_model, changeEvent=request.changeEvent)
    )

    try:
        result = analyze_model(resolved_model, request.changeEvent)
        completed = job_store.complete(job.jobId, result)
        return AnalyzeAcceptedResponse(jobId=completed.jobId, status=completed.status)
    except Exception:
        failed = job_store.fail(job.jobId)
        return AnalyzeAcceptedResponse(jobId=failed.jobId, status=failed.status)


@app.get("/datasets", response_model=DatasetsResponse)
def get_datasets() -> DatasetsResponse:
    return DatasetsResponse(datasets=list_dataset_options())


@app.get("/presets", response_model=PresetsResponse)
def get_presets() -> PresetsResponse:
    return PresetsResponse(presets=list_change_presets())


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Unknown jobId '{job_id}'")
    return job
