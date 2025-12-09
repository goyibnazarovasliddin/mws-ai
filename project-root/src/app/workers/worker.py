"""
Background worker entrypoint.

Vazifasi:
- Celery worker yoki RQ worker tayyorlaydigan skript.
- tasks.py ichidagi funksiyalarni process qiladi.

Bog'lanish:
- docker-compose.yml ichida `worker` servisi sifatida ishlatiladi (agar asinxron arxitektura bo‘lsa).
"""
