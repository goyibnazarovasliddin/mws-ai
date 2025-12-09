# MWS Backend — Umumiy Overview (Qisqa, ammo keng qamrovli)

Ushbu backend xizmati — dasturiy ta’minot xavfsizligi jarayonida ishlatiladigan secret-skanner vositalari (Gitleaks, TruffleHog, GitGuardian va boshqalar) natijalarini avtomatlashtirilgan tarzda tahlil qilish va ularning ichida aynan haqiqiy xavf tug‘diruvchi sirlarni ajratib olish uchun mo‘ljallangan.

An’anaviy skannerlar faqat regex yoki pattern asosida ishlaydi. Shu sababli ular juda ko‘p false-positive natijalar qaytaradi. Masalan:
- test yoki mock fayllardagi sun’iy tokenlar,
- “example”, “fake”, “placeholder” kabi soxta qiymatlar,
- avtomatik generatsiya qilingan past entropiyali satrlar,
- vaqtinchalik konfiguratsiya kodlari.

Bu esa DevSecOps jamoalari uchun juda katta vaqt sarfi va ortiqcha yuk bo‘lishiga olib keladi.  
Secret Filter Backend ana shu muammoni engillashtiradi va asosiy tekshiruv jarayonlarini aqlli tarzda avtomatlashtiradi.

Quyidagi ko‘p bosqichli pipeline asosida ishlaydi:

1. SARIF yoki JSON formatdagi skanerlash natijalarini qabul qiladi va yagona formatga normalizatsiya qiladi.  
2. Deterministik qoidalar asosida eng oddiy false-positive topilmalarni darhol filtrlab tashlaydi (test/ kataloglari, placeholder so‘zlari, past entropiya va h.k.).  
3. Murakkabroq holatlar uchun ML modeli features orqali baho beradi (masalan: snippet uzunligi, yo‘l signali, entropiya, regex mosligi).  
4. ML ishonchi past bo‘lsa, LLM (OpenAI API yoki mos model) kontekstni chuqur tahlil qilib yakuniy qaror chiqaradi.  
5. Kerak bo‘lganda Active Verification moduli orqali API tokenlarining haqiqiyligi mock yoki real provayderlar yordamida tekshiriladi (masalan AWS token validatsiyasi).  
6. Yakunda har bir finding uchun quyidagi ma’lumotlar shakllantiriladi:  
   - false-positive ekanligi yoki yo‘qligi,  
   - avtomatlashtirilgan qaror sababi (ai_verdict),  
   - ML/LLM ishonchlilik ko‘rsatkichi (confidence),  
   - asl joylashuvi (original_location),  
   - umumiy statistika (qancha FP filtrlandi, qancha TP qoldi).

Tizim FastAPI asosida qurilgan bo‘lib:
- JWT orqali autentifikatsiya
- Modul asosidagi toza va kengaytiriladigan arxitektura
- SARIF/JSON normalizatsiyasi  
- ML + LLM bilan chuqur tekshiruv
- Workerlar orqali asinxron ishlash imkoniyati
- Frontend yoki CI/CD pipeline bilan osongina integratsiya qilinishi uchun to‘liq REST API

Natijada DevSecOps jamoalari yuzlab natijalarni qo‘lda ko‘rish o‘rniga, faqat haqiqiy xavflarga e’tibor qaratadi.  
Bu esa skanerlash jarayonini tezlashtiradi, noto‘g‘ri ogohlantirishlar sonini kamaytiradi va ishlab chiqish jarayonlarini sekinlashtirmasdan yuqori xavfsizlikni ta’minlaydi.
