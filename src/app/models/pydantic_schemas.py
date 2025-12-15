"""
Pydantic schemas — request/response and validation.

Function:
- Defines the request body and response model for API endpoints:
- AnalyzeRequest, AnalyzeResponse, FindingSchema, ReportSchema, AuthSchemas, etc.

Linkage:
- The api.v1.endpoints.* files import these schemas.
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Auth Schemas ---
class UserBase(BaseModel):
    username: str
    email: EmailStr = None

class UserCreate(UserBase):
    password: str

class UserSchema(UserBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Analysis Schemas ---
class AnalyzeRequest(BaseModel):
    tool: str = "gitleaks"
    report: Dict[str, Any] # Accepts JSON or SARIF structure

class FindingSchema(BaseModel):
    id: Optional[int] = None
    rule_id: str
    file_path: str
    secret_snippet: str
    is_false_positive: bool
    confidence: float
    ai_verdict: str
    original_location: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class AnalyzeResponse(BaseModel):
    report_id: str
    status: str
    findings: List[FindingSchema]
    stats: Dict[str, int]

class ReportSchema(BaseModel):
    id: str
    created_at: datetime
    status: str
    stats: Optional[Dict[str, int]]
    
    class Config:
        from_attributes = True

