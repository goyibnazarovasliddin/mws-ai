"""
Dependency helpers (FastAPI dependency injection).

Function:
- Provides common dependency functions like get_db, get_current_user, require_admin.
- Makes it easy to connect to endpoints using `Depends(get_db)` calls.

Linkage:
- Linked to db/session.py, core/auth.py.
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.db_models import User

# Re-export get_db for convenience if needed, or just use it from session
# But keeping it here consolidates deps
# get_db imported above

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

