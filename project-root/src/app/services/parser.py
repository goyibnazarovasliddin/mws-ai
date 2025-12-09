"""
SARIF va turli scannerlar (gitleaks, trufflehog va boshqalar) formatini normalizatsiya qiluvchi modul.

Vazifasi:
- Turli hisobot formatlarini yagona `Finding` obyektlar ro'yxatiga o'giradi:
  { rule_id, file_path, snippet, original_location, raw_result }

Bog'lanish:
- endpoints/analyze.py bu funksiyani chaqiradi.
- storage.py ga normalized payload saqlanadi.
"""
