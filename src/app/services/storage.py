"""
Data persistence (DB CRUD) helper module.

Task:
- Store, update, read Reports and Findings in DB and calculate statistics.
- Store Feedback and Audit records.

Linkage:
- models/db_models.py works with ORM models.
- endpoints and ml_pipeline refer to this module.
"""

from sqlalchemy.orm import Session
from app.models.db_models import Report, Finding
from app.models.pydantic_schemas import ReportSchema, FindingSchema
import uuid
import datetime

def create_report(db: Session, user_id: int) -> str:
    report_id = str(uuid.uuid4())
    report = Report(
        id=report_id,
        user_id=user_id,
        created_at=datetime.datetime.utcnow(),
        status="processing",
        stats={}
    )
    db.add(report)
    db.commit()
    return report_id

def save_findings(db: Session, report_id: str, findings: list[FindingSchema]):
    db_findings = []
    for f in findings:
        db_f = Finding(
            report_id=report_id,
            unique_hash=f"{f.file_path}:{f.rule_id}:{f.secret_snippet}", # Simple hash
            rule_id=f.rule_id,
            file_path=f.file_path,
            line_number=f.original_location.get("line", 0) if f.original_location else 0,
            secret_snippet=f.secret_snippet,
            is_false_positive=f.is_false_positive,
            confidence=f.confidence,
            ai_verdict=f.ai_verdict,
            raw_data=f.original_location
        )
        db_findings.append(db_f)
    
    db.add_all(db_findings)
    db.commit()

def update_report_status(db: Session, report_id: str, status: str, stats: dict = None):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report:
        report.status = status
        if stats:
            report.stats = stats
        db.commit()

def get_report(db: Session, report_id: str, user_id: int):
    # Ensure user owns the report
    return db.query(Report).filter(Report.id == report_id, Report.user_id == user_id).first()

