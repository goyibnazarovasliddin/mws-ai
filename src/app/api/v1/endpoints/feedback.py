"""
/api/feedback endpoint — receives user feedback.

Task:
- Receives feedback when the user marks "AI verdict wrong".
- The feedback is stored in the `Audit` or `Feedback` table and becomes the dataset for model retraining.

Connection:
- Writes to the DB via services/storage.py.
- ml/train.py can use these feedbacks during retraining.

Note:
- When saving feedback, do not forget to write the user ID and time
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.api.v1 import deps
from app.models.db_models import User, Feedback, Finding

router = APIRouter()

class FeedbackRequest(BaseModel):
    finding_id: int # Database ID of the finding (not the rule_id)
    is_correct: bool
    comment: str = None

@router.post("/")
def submit_feedback(
    feedback_in: FeedbackRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    # Verify finding exists and belongs to user's report (indirectly)
    # Ideally should join Finding -> Report -> User
    finding = db.query(Finding).filter(Finding.id == feedback_in.finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    # Check ownership
    if finding.report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    feedback = Feedback(
        finding_id=feedback_in.finding_id,
        user_id=current_user.id,
        is_correct=feedback_in.is_correct,
        comment=feedback_in.comment
    )
    db.add(feedback)
    db.commit()
    return {"status": "success"}

