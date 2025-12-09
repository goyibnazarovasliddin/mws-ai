"""
DB sessiya yaratuvchi modul.

Vazifasi:
- SQLAlchemy engine va SessionLocal yaratadi.
- `get_db()` dependency (generator) ni taqdim etadi.

Bog'lanish:
- api endpoints `Depends(get_db)` orqali sessiya oladi.
- config.py dagi DATABASE_URL bilan ishlaydi.

E'tibor:
- Hackathon uchun SQLite `sqlite:///./dev.db` ishlatishimiz oson; production uchun esa Postgresga o'tishimiz kerak bo'ladi.
"""
