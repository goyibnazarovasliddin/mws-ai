"""
ORM modellari (SQLAlchemy) — User, Report, Finding, Feedback/Audit va boshqalar.

Vazifasi:
- DB dizaynini shu yerda aniqlash: User, Report (original + normalized), Finding (annotatsiyalar), AuditLog/Feedback.

Bog'lanish:
- db/base.py ichidagi Base bilan ishlaydi.
- services/storage.py CRUD operatsiyalar uchun shu modellardan foydalanadi.

E'tibor:
- Field turlarini aniq belgilash va indekslar qo'yish (report_id, finding_id) kerak.
"""
