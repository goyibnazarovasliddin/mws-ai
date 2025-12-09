"""
Feature extraction modul.

Vazifasi:
- Finding (snippet, file_path va boshqa signallar) dan model uchun kerakli features (xususiyatlar) ishlab chiqadi:
  - entropiya,
  - yo'l signal (test/ mock/),
  - snippet uzunligi,
  - placeholder so'zlar borligi,
  - regex conformity va h.k.

Bog'lanish:
- services/parser.py dan olingan finding obyekti bilan ishlaydi.
- ml/predict.py va ml/train.py tomonidan ishlatiladi.
"""
