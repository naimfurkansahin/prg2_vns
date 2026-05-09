import os
import sys
from dotenv import load_dotenv

# Takım arkadaşlarımızın yazdığı modülleri içeri aktarıyoruz
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
        print("Lütfen projenin ana dizininde bir '.env' dosyası oluşturun ve içine şu satırı ekleyin:")
        print("GROQ_API_KEY=sizin_api_anahtariniz_buraya")
        sys.exit(1) # Anahtar yoksa programı güvenli bir şekilde kapat

    # 2. Veritabanını Hazırla (Melih'in Modülü)
    print("[Sistem] Veritabanı kontrol ediliyor...")
    try:
        database.create_tables()
        print("[Sistem] Veritabanı bağlantısı başarılı.")
    except Exception as e:
        print(f"[HATA] Veritabanı oluşturulurken bir sorun yaşandı: {e}")
        sys.exit(1)

    # 3. Yapay Zeka Motorunu Başlat (Senin Modülün)
    # Bilgisayarının gücüne göre "medium", "small" veya "base" yapabilirsin.
    print("[Sistem] Yapay Zeka Motoru yükleniyor, lütfen bekleyin...")
    engine = VNSEngine(groq_api_key=api_key, model_size="medium", device="cpu")

    # 4. Arayüzü Başlat ve Motoru Enjekte Et (Betül'ün Modülü)
    print("[Sistem] Kullanıcı arayüzü başlatılıyor...")
    try:
        app = VNSApp(engine=engine)
        app.mainloop()
    except Exception as e:
        print(f"\n[HATA] Arayüz başlatılırken kritik bir hata oluştu: {e}")

if __name__ == "__main__":
    main()