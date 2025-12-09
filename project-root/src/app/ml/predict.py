"""
Model predict wrapper.

Vazifasi:
- ml.model/classifier.pkl faylini yuklaydi (singleton).
- extract qilingan features ni qabul qilib, prob_fp yoki klass natijasini qaytaradi.

Bog'lanish:
- services/ml_pipeline.py orqali chaqiriladi.
- tests/test_ml.py tomonidan unit test qilinadi.

E'tibor:
- Agar model mavjud bo'lmasa, fallback (dummy predict) qaytarish kerak.
"""
