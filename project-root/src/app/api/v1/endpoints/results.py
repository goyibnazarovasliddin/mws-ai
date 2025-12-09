"""
/api/results/{report_id} endpoint — tahlil natijalarini olish.

Vazifasi:
- Saqlangan report_id bo'yicha normalizatsiyalangan va annotatsiyalangan natijalarni qaytaradi.
- Statistika: total_findings, filtered_fp, remaining_tp kabi summary-return.

Bog'lanish:
- services/storage.py orqali DB yoki fayl tizimidan natijalarni o'qiydi.
- Frontend bu endpointni polling bilan yoki websocket orqali sinxronizatsiya qilishi mumkin.

E'tibor:
- Agar analiz async bajarilsa, status maydonini qaytarib, frontend progress ko'rsatishi mumkin.
"""
