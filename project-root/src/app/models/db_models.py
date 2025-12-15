"""
ORM models (SQLAlchemy) — User, Report, Finding, Feedback/Audit, etc.

Task:
- Define DB design here: User, Report (original + normalized), Finding (annotations), AuditLog/Feedback.

Connection:
- Works with Base in db/base.py.
- Uses these models for CRUD operations in services/storage.py.

Note:
- Field types must be explicitly defined and indexes must be set (report_id, finding_id).
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, index=True)  # Use custom ID or UUID
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="pending")  # pending, completed, failed
    stats = Column(JSON, nullable=True)  # Summary stats

    user = relationship("User", back_populates="reports")
    findings = relationship("Finding", back_populates="report")

User.reports = relationship("Report", back_populates="user")

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, ForeignKey("reports.id"))
    unique_hash = Column(String, index=True)  # To identify duplicates
    
    rule_id = Column(String)
    file_path = Column(String)
    line_number = Column(Integer)
    secret_snippet = Column(String)
    
    # Analysis results
    is_false_positive = Column(Boolean, default=False)
    confidence = Column(Float, default=0.0)
    ai_verdict = Column(String, nullable=True) # Explanation
    
    # Original raw data
    raw_data = Column(JSON)
    
    report = relationship("Report", back_populates="findings")
    feedbacks = relationship("Feedback", back_populates="finding")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    is_correct = Column(Boolean) # User says if AI was correct
    comment = Column(String, nullable=True)
    
    finding = relationship("Finding", back_populates="feedbacks")

