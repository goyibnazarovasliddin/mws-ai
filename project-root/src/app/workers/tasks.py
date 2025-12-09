"""
Background tasklar (Celery / RQ uchun).

Vazifasi:
- Uzun davom etadigan ishlarni (ML predict, LLM chaqiruv, active verification) asinxron bajarish uchun tasklarni ta'riflaydi.
- Masalan: `process_report(report_id)` yoki `active_verify(finding_id)`.

Bog'lanish:
- endpoints/analyze.py asinxron ishlashni tanlagan hollarda bu tasklar enque qilinadi.
- worker.py bu tasklarni bajaradi.

E'tibor:
- Celery ishlatilsa, Redis yoki boshqa broker va result backend kerak bo‘ladi.
"""
