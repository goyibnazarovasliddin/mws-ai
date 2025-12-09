"""
Auth core — JWT token yaratish va tekshirish logikasi.

Vazifasi:
- access token yaratish, token refresh, token decoding va user identity olish.
- Parol tekshirish (passlib yordamida) yoki dummy check.

Bog'lanish:
- api.v1.endpoints.auth.py ishlatadi.
- config.py ichidagi JWT_SECRET_KEY va boshqa parametrlarni o'qiydi.

E'tibor:
- Token expiry, algoritm (HS256) va secret saqlashga e'tibor berish kerak.
"""
