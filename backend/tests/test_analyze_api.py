from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_post_analyze_and_get_job() -> None:
    response = client.post(
        "/analyze",
        json={
            "datasetId": "office_core_v1",
            "changeEvent": {
                "type": "MOVE",
                "elementIds": ["A-WALL-01"],
                "delta": {"dx": 0.0, "dy": 0.25}
            }
        }
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["jobId"]
    assert payload["status"] in {"pending", "completed"}

    job_response = client.get(f"/jobs/{payload['jobId']}")
    assert job_response.status_code == 200

    job = job_response.json()
    assert job["status"] == "completed"
    assert job["result"] is not None
    assert job["result"]["summary"]["totalImpacted"] >= 1


def test_inline_dataset_result_order_is_deterministic() -> None:
    inline_dataset = {
        "projectId": "inline",
        "elements": [
            {
                "id": "A-WALL-01",
                "discipline": "ARCH",
                "category": "Wall",
                "level": "L1",
                "bbox": {"x1": 0, "y1": 0, "x2": 8, "y2": 0.3},
                "connectors": [],
                "params": {}
            },
            {
                "id": "M-DUCT-01",
                "discipline": "MECH",
                "category": "Duct",
                "level": "L1",
                "bbox": {"x1": 2, "y1": 0.2, "x2": 4, "y2": 0.6},
                "connectors": ["C-X"],
                "params": {}
            },
            {
                "id": "E-TRAY-01",
                "discipline": "ELEC",
                "category": "CableTray",
                "level": "L1",
                "bbox": {"x1": 4, "y1": 0.1, "x2": 7, "y2": 0.25},
                "connectors": ["C-X"],
                "params": {}
            }
        ]
    }

    request = {
        "datasetJson": inline_dataset,
        "changeEvent": {
            "type": "MOVE",
            "elementIds": ["A-WALL-01"],
            "delta": {"dx": 0.0, "dy": 0.2}
        }
    }

    first = client.post("/analyze", json=request).json()
    second = client.post("/analyze", json=request).json()

    first_job = client.get(f"/jobs/{first['jobId']}").json()
    second_job = client.get(f"/jobs/{second['jobId']}").json()

    first_ids = [item["id"] for item in first_job["result"]["impactedElements"]]
    second_ids = [item["id"] for item in second_job["result"]["impactedElements"]]

    assert first_ids == second_ids


def test_get_unknown_job_returns_404() -> None:
    response = client.get("/jobs/not-a-job")
    assert response.status_code == 404


def test_catalog_endpoints_return_datasets_and_presets() -> None:
    datasets_response = client.get("/datasets")
    assert datasets_response.status_code == 200
    datasets = datasets_response.json()["datasets"]
    assert len(datasets) >= 2

    dataset_ids = {dataset["id"] for dataset in datasets}
    assert "office_core_v1" in dataset_ids
    assert "clinic_floor_v1" in dataset_ids

    presets_response = client.get("/presets")
    assert presets_response.status_code == 200
    presets = presets_response.json()["presets"]
    assert len(presets) >= 3

    for preset in presets:
        assert preset["datasetId"] in dataset_ids
