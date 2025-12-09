"""
Ilovaning konfiguratsiya sozlamalari (Pydantic BaseSettings).

Vazifasi:
- .env faylidan / env o'zgaruvchilardan sozlamalarni yuklaydi:
  DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY va boshqalar.

Bog'lanish:
- main.py, db/session.py, services/llm_client.py va auth modullar tomonidan ishlatiladi.

E'tibor:
- Maxfiy kalitlarni (OPENAI_API_KEY, JWT_SECRET_KEY) .env faylga qo'ying va Git-ga push qilmang.
"""