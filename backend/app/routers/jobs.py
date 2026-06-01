import subprocess
import sys
import os
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from app.cache import cache_flush_pattern

router = APIRouter(prefix="/api/v1", tags=["jobs"])

# Track job status in memory (sufficient for MVP — no persistence needed)
_job_status: dict = {
    "last_run": None,
    "status": "idle",        # idle | running | completed | failed
    "message": None,
}


class JobStatus(BaseModel):
    status: str
    last_run: str | None
    message: str | None


def _run_valuation_job():
    """Runs in background thread via BackgroundTasks."""
    global _job_status
    _job_status["status"] = "running"
    _job_status["message"] = "Valuation pipeline running..."

    try:
        # Get the repo root (two levels up from backend/app/routers/)
        repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../")
        )
        script = os.path.join(repo_root, "data", "valuate.py")

        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=repo_root,
        )

        if result.returncode == 0:
            _job_status["status"] = "completed"
            _job_status["message"] = "Valuation pipeline completed successfully"
        else:
            _job_status["status"] = "failed"
            _job_status["message"] = result.stderr[-500:] if result.stderr else "Unknown error"

    except subprocess.TimeoutExpired:
        _job_status["status"] = "failed"
        _job_status["message"] = "Job timed out after 120 seconds"
    except Exception as e:
        _job_status["status"] = "failed"
        _job_status["message"] = str(e)
    finally:
        _job_status["last_run"] = datetime.now(timezone.utc).isoformat()


@router.post("/jobs/valuate")
def trigger_valuation(background_tasks: BackgroundTasks):
    """Trigger the valuation pipeline as a background job."""
    if _job_status["status"] == "running":
        raise HTTPException(status_code=409, detail="Valuation job is already running")

    background_tasks.add_task(_run_valuation_job)
    _job_status["status"] = "running"
    _job_status["last_run"] = None

    return {"message": "Valuation job started", "status": "running"}


@router.get("/jobs/valuate/status", response_model=JobStatus)
def get_job_status():
    """Get the status of the last valuation job."""
    return JobStatus(
        status=_job_status["status"],
        last_run=_job_status["last_run"],
        message=_job_status["message"],
    )

@router.delete("/cache")
def clear_cache():
    """Clear all LuxeMarket cache entries. Dev/admin use only."""
    count = cache_flush_pattern("luxemarket:*")
    return {"message": f"Cleared {count} cache keys"}
