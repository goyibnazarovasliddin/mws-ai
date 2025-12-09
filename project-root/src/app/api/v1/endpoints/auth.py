"""
/api/auth/* endpointlari — autentifikatsiya va tokenlarni boshqarish.

Vazifasi:
- /login, /refresh kabi endpointlar orqali JWT access/refresh tokenlar beradi.
- Bu tokenlar keyingi so'rovlarda Authorization: Bearer <token> sifatida uzatiladi.

Bog'lanish:
- core/auth.py va core/security.py bilan ishlaydi.
- DB bilan bog'lanish orqali real foydalanuvchi tekshiruvi amalga oshiriladi (User modeli).

E'tibor:
- Hozirchalik uchun minimal dummy auth (static token) bilan boshlash mumkin, lekin production uchun parol hashing (bcrypt) va to'liq user management kerak.
"""
