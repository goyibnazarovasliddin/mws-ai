"""
DB initialization script.

Task:
- Run Alembic migrations or create tables via SQLAlchemy (Base.metadata.create_all).
- Scripts can be called to seed demo data.

Auto-generated:
- If `Base.metadata.create_all()` is called, the `dev.db` (SQLite) file will be automatically created when this script is run.

Note:
- For production, Alembic migration is recommended — `alembic revision --autogenerate` and `alembic upgrade head`.
"""

# not used yet