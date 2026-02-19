from __future__ import annotations

from threading import Lock
from uuid import uuid4

from .schema import AnalyzeResult, JobRequestEcho, JobResponse


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobResponse] = {}
        self._lock = Lock()

    def create(self, request: JobRequestEcho) -> JobResponse:
        job_id = uuid4().hex[:12]
        job = JobResponse(jobId=job_id, status="pending", request=request, result=None)
        with self._lock:
            self._jobs[job_id] = job
        return job

    def complete(self, job_id: str, result: AnalyzeResult) -> JobResponse:
        with self._lock:
            job = self._jobs[job_id]
            job.status = "completed"
            job.result = result
            self._jobs[job_id] = job
            return job

    def fail(self, job_id: str) -> JobResponse:
        with self._lock:
            job = self._jobs[job_id]
            job.status = "failed"
            self._jobs[job_id] = job
            return job

    def get(self, job_id: str) -> JobResponse | None:
        with self._lock:
            return self._jobs.get(job_id)


job_store = InMemoryJobStore()
