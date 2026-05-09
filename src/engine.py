import os
from dotenv import load_dotenv
from faster_whisper import WhisperModel
from groq import Groq

class VNSEngine:
    # Parametreleri dışarıdan alınabilir hale getirdik (Esneklik)
    def __init__(self, groq_api_key, model_size="medium", device="cpu"):
        print("[Sistem] Motor başlatılıyor...")
        self.model_size = model_size 
        
        try:
            print(f"[Sistem] Faster-Whisper ({self.model_size} model, {device}) yükleniyor...")
            # compute_type'ı int8 bıraktık, CPU için en stabilidir. GPU için "float16" da eklenebilir ileride.
            self.whisper_model = WhisperModel(self.model_size, device=device, compute_type="int8")
        except Exception as e:
            print(f"[HATA] Whisper modeli yüklenirken bir sorun oluştu: {e}")

        # Groq API Kurulumu
        try:
            self.groq_client = Groq(api_key=groq_api_key)
            print("[Sistem] Motor hazır!\n" + "-"*40)
        except Exception as e:
            print(f"[HATA] Groq API başlatılamadı: {e}")

    def transcribe_audio(self, audio_path, language="tr"):
        print(f"[STT] '{audio_path}' deşifre ediliyor...")
        try:
            # Dili de opsiyonel yaptık
            segments, info = self.whisper_model.transcribe(audio_path, beam_size=5, language=language)
            full_text = " ".join([segment.text for segment in segments])
            return full_text.strip()
        except Exception as e:
            print(f"[HATA] Deşifre işlemi başarısız: {e}")
            return ""

    def analyze_text(self, text):
        # Boş metin kontrolü
        if not text or len(text.strip()) == 0:
            return "[Uyarı] Analiz edilecek metin bulunamadı."

        print("[NLP] Metin Groq (Llama 3) ile analiz ediliyor...")
        try:
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
        except Exception as e:
            error_msg = f"[HATA] Yapay zeka analizi sırasında bir sorun oluştu: {e}"
            print(error_msg)
            return error_msg

# ==========================================
# TEST ALANI
# ==========================================
if __name__ == "__main__":
    load_dotenv() 
    
    API_KEY = os.environ.get("GROQ_API_KEY") 
    
    if not API_KEY:
        print("[HATA] API Anahtarı bulunamadı! Lütfen .env dosyanızı kontrol edin.")
    else:
        # Test ederken CPU kullandığımızı açıkça belirtiyoruz
        engine = VNSEngine(groq_api_key=API_KEY, model_size="medium", device="cpu")
    
        test_dosyasi = "test_sesi.mp3" 
    
        if os.path.exists(test_dosyasi):
            metin = engine.transcribe_audio(test_dosyasi)
            print("\n--- DEŞİFRE SONUCU ---")
            print(metin)
            
            # Eğer metin boş dönmediyse analiz et
            if metin:
                analiz = engine.analyze_text(metin)
                print("\n--- YAPAY ZEKA ANALİZİ ---")
                print(analiz)
        else:
            print(f"\n[HATA] '{test_dosyasi}' bulunamadı! Lütfen test için projeye bir ses dosyası ekle.")