"""
Dependency helpers (FastAPI dependency injection).

Vazifasi:
- get_db, get_current_user, require_admin kabi umumiy dependency funksiyalarni taqdim etadi.
- Endpoints ichida `Depends(get_db)` kabi chaqiruvlar orqali ulangani oson bo‘ladi.

Bog'lanish:
- db/session.py, core/auth.py bilan bog'liq.
"""
