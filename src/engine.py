# -*- coding: utf-8 -*-
import os
import sys
import io
from faster_whisper import WhisperModel
from groq import Groq

# Çıkış güvenliğini burada da sağlıyoruz (tekil çalıştırma için)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class VNSEngine:
    def __init__(self, groq_api_key, model_size="medium", device="cpu"):
        print("[Sistem] Motor başlatılıyor...")
        self.model_size = model_size 
        
        try:
            print(f"[Sistem] Faster-Whisper ({self.model_size} model) yükleniyor...")
            self.whisper_model = WhisperModel(self.model_size, device=device, compute_type="int8")
        except Exception as e:
            # str(e) yerine repr(e) kullanımı karakter hatalarını önler
            print(f"[HATA] Whisper modeli yüklenirken bir sorun oluştu: {repr(e)}")

        try:
            self.groq_client = Groq(api_key=groq_api_key)
            print("[Sistem] Motor hazır!\n" + "-"*40)
        except Exception as e:
            print(f"[HATA] Groq API başlatılamadı: {repr(e)}")

    def transcribe_audio(self, audio_path, language="tr"):
        print(f"[STT] '{audio_path}' deşifre ediliyor...")
        try:
            segments, info = self.whisper_model.transcribe(audio_path, beam_size=5, language=language)
            full_text = " ".join([segment.text for segment in segments])
            return full_text.strip()
        except Exception as e:
            print(f"[HATA] Deşifre işlemi başarısız: {repr(e)}")
            return ""

    def analyze_text(self, text):
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
            # Hata mesajını değişkene alıp güvenli şekilde döndürüyoruz
            error_info = repr(e)
            error_msg = f"[HATA] Yapay zeka analizi sırasında bir sorun oluştu: {error_info}"
            print(error_msg)
            return error_msg

if __name__ == "__main__":
    # Test amaçlı direkt çalıştırma için
    print("[Test] Lütfen main.py üzerinden çalıştırın.")