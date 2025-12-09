"""
/api/feedback endpoint — foydalanuvchi fikrlarini qabul qilish.

Vazifasi:
- Foydalanuvchi "AI verdict noto'g'ri" deb belgilasa, feedback qabul qiladi.
- Feedbacklar `Audit` yoki `Feedback` jadvaliga saqlanadi va model retrain uchun dataset bo‘ladi.

Bog'lanish:
- services/storage.py orqali DB-ga yozadi.
- ml/train.py retrain jarayonida ushbu feedbacklardan foydalanishi mumkin.

E'tibor:
- Feedbackni saqlashda foydalanuvchi identifikatorini va vaqtni yozishni unutmaslik kerak
"""
