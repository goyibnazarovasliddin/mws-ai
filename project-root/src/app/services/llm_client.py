"""
LLM (OpenAI yoki boshqalar) bilan ishlovchi wrapper.

Vazifasi:
- LLM prompt templatelarini saqlaydi va OpenAI/other API orqali so'rov yuboradi.
- LLM natijasini JSON pars qiladi va standart formatga keltiradi:
  { "false_positive": bool, "reason": str, "confidence": float }

Bog'lanish:
- services/ml_pipeline.py yoki endpoints/analyze.py da murakkab holatlar uchun chaqiriladi.
- config.py orqali OPENAI_API_KEY o'qiladi.

E'tibor:
- LLM chaqiruvlarining xarajatlarini hisobga olish kerak. Hackathon uchun minimal token limit bilan sinov qilamiz.
- Natijalar ishonchlilik darajasini saqlashga harakat qilish kerak.
"""
