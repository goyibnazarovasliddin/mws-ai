"""
/api/results/{report_id} endpoint — retrieves analysis results.

Function:
- Returns normalized and annotated results based on the stored report_id.
- Statistics: summary-return like total_findings, filtered_fp, remaining_tp.

Connection:
- Reads results from DB or filesystem via services/storage.py.
- Frontend can synchronize this endpoint by polling or via websocket.

Note:
- If analysis is performed async, it can return a status field and show progress on frontend.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.v1 import deps
from app.models.db_models import User
from app.models.pydantic_schemas import AnalyzeResponse, FindingSchema
from app.services import storage

router = APIRouter()

@router.get("/{report_id}", response_model=AnalyzeResponse)
def get_results(
    report_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    report = storage.get_report(db, report_id, current_user.id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    findings_schema = []
    if report.findings:
        for f in report.findings:
            findings_schema.append(FindingSchema(
                id=f.id,
                rule_id=f.rule_id,
                file_path=f.file_path,
                secret_snippet=f.secret_snippet,
                is_false_positive=f.is_false_positive,
                confidence=f.confidence,
                ai_verdict=f.ai_verdict or "",
                original_location=f.raw_data
            ))
            
    return {
        "report_id": report.id,
        "status": report.status,
        "findings": findings_schema,
        "stats": report.stats or {}
    }

