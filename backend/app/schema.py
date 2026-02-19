from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


Discipline = Literal["ARCH", "MECH", "ELEC", "PLUMB"]
ChangeType = Literal["MOVE", "RESIZE", "RELOCATE"]
JobStatus = Literal["pending", "completed", "failed"]


class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

    @model_validator(mode="after")
    def validate_box(self) -> "BBox":
        if self.x1 >= self.x2:
            raise ValueError("bbox.x1 must be < bbox.x2")
        if self.y1 >= self.y2:
            raise ValueError("bbox.y1 must be < bbox.y2")
        return self


class Element(BaseModel):
    id: str
    discipline: Discipline
    category: str
    level: str
    bbox: BBox
    connectors: list[str] = Field(default_factory=list)
    params: dict[str, Any] = Field(default_factory=dict)


class ChangeDelta(BaseModel):
    dx: float
    dy: float


class ChangeEvent(BaseModel):
    type: ChangeType
    elementIds: list[str] = Field(min_length=1)
    delta: ChangeDelta | None = None
    newBbox: BBox | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DatasetOption(BaseModel):
    id: str
    label: str
    description: str


class DatasetsResponse(BaseModel):
    datasets: list[DatasetOption]


class ChangePreset(BaseModel):
    id: str
    datasetId: str
    label: str
    description: str
    changeEvent: ChangeEvent


class PresetsResponse(BaseModel):
    presets: list[ChangePreset]


class ProjectModel(BaseModel):
    projectId: str
    elements: list[Element]


class AnalyzeRequest(BaseModel):
    datasetId: str | None = None
    datasetJson: ProjectModel | None = None
    changeEvent: ChangeEvent

    @model_validator(mode="after")
    def validate_dataset_source(self) -> "AnalyzeRequest":
        has_dataset_id = self.datasetId is not None
        has_dataset_json = self.datasetJson is not None
        if has_dataset_id == has_dataset_json:
            raise ValueError("Exactly one of datasetId or datasetJson must be provided")
        return self


class ImpactReason(BaseModel):
    ruleId: Literal["intersection", "clearance", "connector"]
    description: str
    pathElementIds: list[str] = Field(min_length=2)


class ImpactedElement(BaseModel):
    id: str
    discipline: Discipline
    category: str
    severity: float
    reasons: list[ImpactReason]


class AnalyzeSummary(BaseModel):
    totalImpacted: int
    byDiscipline: dict[Discipline, int]
    maxSeverity: float


class AnalyzeResult(BaseModel):
    impactedElements: list[ImpactedElement]
    summary: AnalyzeSummary


class AnalyzeAcceptedResponse(BaseModel):
    jobId: str
    status: JobStatus


class JobRequestEcho(BaseModel):
    datasetId: str
    resolvedModel: ProjectModel
    changeEvent: ChangeEvent


class JobResponse(BaseModel):
    jobId: str
    status: JobStatus
    request: JobRequestEcho
    result: AnalyzeResult | None = None
