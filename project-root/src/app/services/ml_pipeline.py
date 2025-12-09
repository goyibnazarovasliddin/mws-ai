"""
ML pipeline va biznes logikasi.

Vazifasi:
- Parserdan olingan findinglarni qabul qilib:
  1) rule_filter orqali obvious FP larni ajratadi,
  2) ml.features.extract_features() orqali feature oladi,
  3) ml.predict.predict() orqali ehtimolni oladi,
  4) ambivalent holatlar uchun llm_client dan so'raydi,
  5) active verification kerak bo'lsa verifier.py chaqiradi,
  6) yakuniy annotated findingni storage ga yozadi.

Bog'lanish:
- services/parser.py, services/rule_filter.py, services/llm_client.py, ml/* va services/storage.py bilan bog'langan.
"""
