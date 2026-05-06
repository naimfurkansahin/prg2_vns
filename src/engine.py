import os
from dotenv import load_dotenv
from faster_whisper import WhisperModel
from groq import Groq

class VNSEngine:
    def __init__(self, groq_api_key):
        print("[Sistem] Motor başlatılıyor...")
        # Faster-Whisper Kurulumu (Lokal)
        self.model_size = "medium" # Bilgisayarın güçlüyse "small" veya "medium" yapabilirsin
        print(f"[Sistem] Faster-Whisper ({self.model_size} model) yükleniyor...")
        self.whisper_model = WhisperModel(self.model_size, device="cpu", compute_type="int8")

        # Groq API Kurulumu (Bulut)
        self.groq_client = Groq(api_key=groq_api_key)
        print("[Sistem] Motor hazır!\n" + "-"*40)

    def transcribe_audio(self, audio_path):
        print(f"[STT] '{audio_path}' deşifre ediliyor...")
        segments, info = self.whisper_model.transcribe(audio_path, beam_size=5, language="tr")
        full_text = " ".join([segment.text for segment in segments])
        return full_text

    def analyze_text(self, text):
        print("[NLP] Metin Groq (Llama 3) ile analiz ediliyor...")
        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Sen profesyonel bir asistansın. Sana verilen metni önce kısaca özetle, ardından en önemli 3 maddeyi çıkar."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            model="llama-3.1-8b-instant", 
        )
        return chat_completion.choices[0].message.content

# ==========================================
# TEST ALANI (Sadece bu dosya çalıştırıldığında burası tetiklenir)
# ==========================================
if __name__ == "__main__":
    # Kasadaki şifreleri sisteme yükle
    load_dotenv() 
    
    # Şifreyi direkt koddan değil, .env içinden güvenle çek
    API_KEY = os.environ.get("GROQ_API_KEY") 
    
    if not API_KEY:
        print("[HATA] API Anahtarı bulunamadı! Lütfen .env dosyanızı kontrol edin.")
    else:
        # Motoru çalıştır
        engine = VNSEngine(groq_api_key=API_KEY)
    
        # Test için proje klasöründe 'test_sesi.mp3' adında kısa bir ses dosyası olmalı
        test_dosyasi = "test_sesi.mp3" 
    
        if os.path.exists(test_dosyasi):
            # 1. Aşama: Sesi Metne Çevir
            metin = engine.transcribe_audio(test_dosyasi)
            print("\n--- DEŞİFRE SONUCU ---")
            print(metin)
        
            # 2. Aşama: Metni Analiz Et
            analiz = engine.analyze_text(metin)
            print("\n--- YAPAY ZEKA ANALİZİ ---")
            print(analiz)
        else:
            print(f"\n[HATA] '{test_dosyasi}' bulunamadı! Lütfen test için projeye bir ses dosyası ekle.")