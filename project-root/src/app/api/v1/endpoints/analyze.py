"""
/api/analyze endpoint — tahlil so'rovlarini qabul qilish.

Vazifasi:
- POST so'rovlarini qabul qiladi: tool (gitleaks) va report (SARIF yoki JSON).
- Kelgan hisobotni parser.normalize orqali normalizatsiya qiladi va Report/Finding formatiga o'zgartiradi.
- Deterministik filterlarni (`rule_filter`) bajaradi.
- ML/LLM yoki background workerga topshiradi (synchronous yoki asynchronous rejim).
- report_id qaytaradi (processing yoki completed status bilan).

Bog'lanish:
- services/parser.py, services/rule_filter.py, services/ml_pipeline.py, services/storage.py va workers/tasks.py bilan ishlaydi.
- Auth: JWT (auth.py yoki deps.py orqali kerak bo‘ladi).

E'tibor:
- Katta fayllarni to‘g‘ridan-to‘g‘ri sinxron qayta ishlash serverni tiqishtirishi mumkin shuning uchun background task (Celery/RQ) tavsiya etiladi.
"""
