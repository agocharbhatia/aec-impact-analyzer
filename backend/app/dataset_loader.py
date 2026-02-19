from __future__ import annotations

import json
from pathlib import Path

from fastapi import HTTPException

from .schema import ChangePreset, DatasetOption, ProjectModel


REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = REPO_ROOT / "shared" / "data" / "datasets"
PRESET_PATH = REPO_ROOT / "shared" / "data" / "change-events" / "presets.json"

DATASET_DESCRIPTIONS: dict[str, str] = {
    "office_core_v1": "Commercial office core with dense MEP distribution around corridor walls.",
    "clinic_floor_v1": "Clinical floor plate with RTU, panels, trays, and branch plumbing dependencies.",
    "mixed_use_lobby_v1": "Mixed-use podium lobby with central plant equipment and multi-trade branch systems.",
    "data_center_pod_v1": "Data center pod with CRAH, busway, and condenser loop dependencies.",
    "residential_tower_l2_v1": "Residential tower floor with FCUs, corridor tray runs, and vertical riser services.",
}


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_dataset_by_id(dataset_id: str) -> ProjectModel:
    normalized = dataset_id.removesuffix(".json")
    path = DATASET_DIR / f"{normalized}.json"

    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Unknown datasetId '{dataset_id}'")

    payload = _read_json(path)

    return ProjectModel(projectId=payload["projectId"], elements=payload["elements"])


def list_dataset_options() -> list[DatasetOption]:
    options: list[DatasetOption] = []
    for path in sorted(DATASET_DIR.glob("*.json")):
        payload = _read_json(path)
        dataset_id = payload.get("datasetId", path.stem)
        label = payload.get("name", dataset_id.replace("_", " ").title())
        description = DATASET_DESCRIPTIONS.get(dataset_id, f"Sample project model ({len(payload.get('elements', []))} elements).")
        options.append(DatasetOption(id=dataset_id, label=label, description=description))
    return options


def list_change_presets() -> list[ChangePreset]:
    payload = _read_json(PRESET_PATH)
    presets = payload.get("presets", [])
    return [ChangePreset.model_validate(item) for item in presets]
