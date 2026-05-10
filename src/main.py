# -*- coding: utf-8 -*-
import os
import sys
import io

# --- KRİTİK: DİĞER IMPORTLARDAN ÖNCE YAPILMALI ---
# Python'ı ve Windows Terminalini UTF-8 moduna zorla
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
# OpenMP çakışma hatasını engelle
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Çıkışı zorla UTF-8 yap (Hataları önlemek için 'replace' modu eklendi)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
from engine import VNSEngine
import database
from ui import VNSApp

def main():
    print("="*50)
    print("VNS: AKILLI SES DEŞİFRE SİSTEMİ BAŞLATILIYOR...")
    print("="*50)

    # 1. Çevresel Değişkenleri Yükle (.env)
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        print("\n[KRİTİK HATA] GROQ_API_KEY bulunamadı!")
        print("Lütfen projenin ana dizininde bir '.env' dosyası oluşturun.")
        sys.exit(1)

    # 2. Veritabanını Hazırla
    print("[Sistem] Veritabanı kontrol ediliyor...")
    try:
        database.create_tables()
        print("[Sistem] Veritabanı bağlantısı başarılı.")
    except Exception as e:
        # repr(e) kullanarak o meşhur karakter hatasını bypass ediyoruz
        print(f"[HATA] Veritabanı oluşturulurken bir sorun yaşandı: {repr(e)}")
        sys.exit(1)

    # 3. Yapay Zeka Motorunu Başlat
    print("[Sistem] Yapay Zeka Motoru yükleniyor, lütfen bekleyin...")
    # Güvenlik için engine başlatmayı try-except içine alıyoruz
    try:
        engine = VNSEngine(groq_api_key=api_key, model_size="medium", device="cpu")
    except Exception as e:
        print(f"[KRİTİK HATA] Motor başlatılamadı: {repr(e)}")
        sys.exit(1)

    # 4. Arayüzü Başlat
    print("[Sistem] Kullanıcı arayüzü başlatılıyor...")
    try:
        app = VNSApp(engine=engine)
        app.mainloop()
    except Exception as e:
        print(f"\n[HATA] Arayüz başlatılırken kritik bir hata oluştu: {repr(e)}")

if __name__ == "__main__":
    main()