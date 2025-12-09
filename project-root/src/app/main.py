"""
FastAPI ilovasining entrypoint fayli.

Vazifasi:
- FastAPI ilovasini yaratadi va routerlarni mount qiladi.
- Global middleware, exception handlerlar va startup/shutdown hodisalarini ro'yxatdan o'tkazadi.

Bog'lanish:
- api.v1.endpoints ichidagi barcha endpoint fayllarini (analyze, results, auth, feedback) import qiladi.
- config.py orqali muhit sozlamalarini o'qiydi.

E'tibor:
- Lokal rivojlanishda `uvicorn src.app.main:app --reload` bilan ishga tushiriladi.
- Production uchun Uvicorn + Gunicorn yoki ASGI serverni reverse-proxyning orqasida ishlating.
"""
