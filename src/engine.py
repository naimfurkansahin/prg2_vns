import os
from faster_whisper import WhisperModel
from groq import Groq

class VNSEngine:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        """
        VNS Motorunu başlatır. 
        model_size: 'base', 'small', 'medium' (Bilgisayarın gücüne göre seçilebilir)
        """
        print(f"Sistem başlatılıyor... Model: {model_size}")
        # Yerel STT Modelini yükle
        self.stt_model = WhisperModel(model_size, device=device, compute_type=compute_type)
        
        # Groq API İstemcisi (API Key'i .env dosyasından almalı veya güvenli bir yerde tutmalısın)
        # Şimdilik buraya 'YOUR_API_KEY' yazıyorum, ilerde .env'ye taşıyalım.
        self.groq_client = Groq(api_key="gsk_DmfAUQPIpoYRnnkY6XysWGdyb3FYvjG9DmPwE2nvp0WliKsz3i4UAIzaSyAlcPrF2ebB0TmuVYtGdPop7VyBiOxaVA4")

    def transcribe_audio(self, audio_path):
        """
        Ses dosyasını metne çevirir. (Yerelde çalışır)
        """
        print("Deşifre işlemi başladı, lütfen bekleyin...")
        segments, info = self.stt_model.transcribe(audio_path, beam_size=5)
        
        full_text = ""
        for segment in segments:
            full_text += f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}\n"
        
        print("Deşifre tamamlandı.")
        return full_text

    def analyze_text(self, text):
        """
        Deşifre edilen metni Groq (Llama 3) ile analiz eder ve özetler.
        """
        print("Analiz yapılıyor...")
        prompt = f"""
        Aşağıdaki ses deşifre metnini analiz et:
        1. Önemli anahtar kelimeleri çıkar.
        2. Konuşmanın kısa bir özetini yap.
        3. Varsa yapılacak işleri (action items) listele.

        Metin:
        {text}
        """

        try:
            completion = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Analiz sırasında bir hata oluştu: {str(e)}"

# --- Test Alanı ---
# Bu dosya doğrudan çalıştırılırsa test yapar
if __name__ == "__main__":
    # Test için örnek bir ses dosyası yolu
    # engine = VNSEngine()
    # text = engine.transcribe_audio("test_ses.mp3")
    # print(text)
    # analysis = engine.analyze_text(text)
    # print(analysis)
    pass