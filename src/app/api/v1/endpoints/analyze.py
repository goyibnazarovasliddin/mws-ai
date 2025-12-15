"""
/api/analyze endpoint — accepts analysis requests.

Function:
- Accepts POST requests: tool (gitleaks) and report (SARIF or JSON).
- Normalizes the incoming report using parser.normalize and converts it to Report/Finding format.
- Performs deterministic filters (`rule_filter`).
- Assigns to ML/LLM or background worker (synchronous or asynchronous mode).
- Returns report_id (with processing or completed status).

Connection:
- Works with services/parser.py, services/rule_filter.py, services/ml_pipeline.py, services/storage.py and workers/tasks.py.
- Auth: JWT (required via auth.py or deps.py).

Note:
- Direct synchronous processing of large files can overload the server, so a background task (Celery/RQ) is recommended will be.
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.v1 import deps
from app.models.pydantic_schemas import AnalyzeRequest, AnalyzeResponse, FindingSchema
from app.models.db_models import User
from app.services import storage, ml_pipeline

router = APIRouter()

@router.post("/", response_model=AnalyzeResponse)
def analyze_report(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    # 1. Create Report ID
    report_id = storage.create_report(db, current_user.id)
    
    # 2. Process Sync (Switch to background_tasks.add_task for async)
    # For prototype, we do it sync to return results immediately if fast enough.
    # But usually user wants immediate ID.
    # Let's do SYNC for now to make sure user sees results in one go for simple demo.
    stats = ml_pipeline.process_report(db, request.tool, request.report, report_id)
    
    # 3. Fetch Findings to return
    # This is a bit inefficient (write then read), but clean for architecture.
    report = storage.get_report(db, report_id, current_user.id)
    
    # Convert DB findings to Pydantic
    findings_schema = []
    if report.findings:
        for f in report.findings:
            findings_schema.append(FindingSchema(
                rule_id=f.rule_id,
                file_path=f.file_path,
                secret_snippet=f.secret_snippet,
                is_false_positive=f.is_false_positive,
                confidence=f.confidence,
                ai_verdict=f.ai_verdict,
                original_location=f.raw_data
            ))

    return {
        "report_id": report_id,
        "status": "completed",
        "findings": findings_schema,
        "stats": report.stats or stats
    }

