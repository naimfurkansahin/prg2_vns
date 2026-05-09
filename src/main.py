import importlib.util
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "vns.db"
ENV_PATH = BASE_DIR / ".env"
HISTORY_JSON = BASE_DIR / "vns_gecmis.json"


def ensure_environment():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not ENV_PATH.exists():
        ENV_PATH.write_text("# GROQ_API_KEY=your_api_key_here\n", encoding="utf-8")

    if not HISTORY_JSON.exists():
        HISTORY_JSON.write_text("{}", encoding="utf-8")


def load_environment():
    if ENV_PATH.exists() and importlib.util.find_spec("dotenv") is not None:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=ENV_PATH)
        return

    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


class Database:
    def __init__(self, path: Path):
        self.path = path
        self.connection = sqlite3.connect(str(self.path))
        self.connection.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS kayitlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dosya_adi TEXT,
                metin_icerigi TEXT,
                ozet_metni TEXT,
                olusturma_tarihi TEXT
            )
            """
        )
        self.connection.commit()

    def add_record(self, dosya_adi, metin_icerigi, ozet_metni):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO kayitlar (dosya_adi, metin_icerigi, ozet_metni, olusturma_tarihi) VALUES (?, ?, ?, ?)",
            (dosya_adi, metin_icerigi, ozet_metni, datetime.now().isoformat(sep=" ", timespec="seconds")),
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_all_records(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM kayitlar ORDER BY id DESC")
        return cursor.fetchall()

    def get_record_by_id(self, record_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM kayitlar WHERE id = ?", (record_id,))
        return cursor.fetchone()

    def search_records(self, keyword):
        cursor = self.connection.cursor()
        query = "%" + keyword + "%"
        cursor.execute(
            "SELECT * FROM kayitlar WHERE dosya_adi LIKE ? OR metin_icerigi LIKE ? OR ozet_metni LIKE ? ORDER BY id DESC",
            (query, query, query),
        )
        return cursor.fetchall()

    def close(self):
        self.connection.close()


class VNSEngine:
    def __init__(self, groq_api_key=None):
        self.groq_api_key = groq_api_key
        self.whisper_available = importlib.util.find_spec("faster_whisper") is not None
        self.groq_available = importlib.util.find_spec("groq") is not None

        self.whisper_model = None
        self.groq_client = None

        if self.whisper_available:
            from faster_whisper import WhisperModel

            self.whisper_model = WhisperModel("medium", device="cpu", compute_type="int8")

        if self.groq_available and self.groq_api_key:
            from groq import Groq

            self.groq_client = Groq(api_key=self.groq_api_key)

    def can_transcribe(self):
        return self.whisper_available

    def can_analyze(self):
        return self.groq_available and self.groq_client is not None

    def transcribe_audio(self, audio_path: str) -> str:
        if not self.whisper_available:
            raise RuntimeError("Faster-Whisper paketi yüklü değil. `pip install faster-whisper` yükleyin.")

        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Ses dosyası bulunamadı: {audio_path}")

        segments, _ = self.whisper_model.transcribe(audio_path, beam_size=5, language="tr")
        return " ".join(segment.text for segment in segments)

    def analyze_text(self, text: str) -> str:
        if not self.groq_available:
            raise RuntimeError("Groq paketi yüklü değil. `pip install groq` yükleyin.")

        if self.groq_client is None:
            raise RuntimeError("GROQ_API_KEY bulunamadı veya geçersiz. .env dosyanızı kontrol edin.")

        completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Sen profesyonel bir asistansın. Sana verilen metni önce kısaca özetle, ardından en önemli 3 maddeyi çıkar."
                },
                {"role": "user", "content": text},
            ],
            model="llama-3.1-8b-instant",
        )
        return completion.choices[0].message.content


class ConsoleUI:
    def __init__(self, engine: VNSEngine, database: Database):
        self.engine = engine
        self.database = database

    def run(self):
        print("\nVNS: Ses Analiz Sistemine Hoşgeldiniz")
        print("Bu sürümde GUI yerine komut satırı arayüzü kullanılmaktadır.")

        while True:
            print("\n1) Ses dosyası analiz et")
            print("2) Metin gir ve analiz et")
            print("3) Geçmiş kayıtları göster")
            print("4) Kayıt ara")
            print("5) Kayıt detayını göster")
            print("6) Kayıt sil")
            print("7) Çıkış")
            choice = input("Seçiminiz: ").strip()

            if choice == "1":
                self.process_audio()
            elif choice == "2":
                self.process_manual_text()
            elif choice == "3":
                self.show_history()
            elif choice == "4":
                self.search_history()
            elif choice == "5":
                self.show_record_detail()
            elif choice == "6":
                self.delete_record()
            elif choice == "7":
                print("Çıkılıyor...")
                break
            else:
                print("Geçersiz seçim. Tekrar deneyin.")

    def process_audio(self):
        if not self.engine.can_transcribe():
            print("Transkripsiyon yapılamıyor. faster-whisper modülü yüklü değil.")
            return

        path = input("Ses dosyası yolunu girin: ").strip()
        if not path:
            print("Dosya yolu boş bırakılamaz.")
            return

        if not Path(path).exists():
            print(f"Dosya bulunamadı: {path}")
            return

        try:
            transcript = self.engine.transcribe_audio(path)
            print("\n--- DEŞİFRE ---\n")
            print(transcript)

            summary = self._analyze_text_safe(transcript)
            print("\n--- ÖZET ---\n")
            print(summary)

            self.database.add_record(Path(path).name, transcript, summary)
            print("Kayıt veritabanına eklendi.")
        except Exception as exc:
            print(f"Hata: {exc}")

    def process_manual_text(self):
        text = input("Analiz edilecek metni girin: ").strip()
        if not text:
            print("Metin boş olamaz.")
            return

        summary = self._analyze_text_safe(text)
        print("\n--- ÖZET ---\n")
        print(summary)

        self.database.add_record("manuel_girdi", text, summary)
        print("Kayıt veritabanına eklendi.")

    def show_history(self):
        records = self.database.get_all_records()
        if not records:
            print("Kayıt bulunamadı.")
            return

        for row in records:
            print(f"[{row['id']}] {row['dosya_adi']} - {row['olusturma_tarihi']}")

    def search_history(self):
        keyword = input("Aranacak kelime: ").strip()
        if not keyword:
            print("Arama kelimesi boş olamaz.")
            return

        records = self.database.search_records(keyword)
        if not records:
            print("Eşleşen kayıt bulunamadı.")
            return

        for row in records:
            print(f"[{row['id']}] {row['dosya_adi']} - {row['olusturma_tarihi']}")

    def show_record_detail(self):
        record_id = input("Gösterilecek kayıt ID'si: ").strip()
        if not record_id.isdigit():
            print("Lütfen geçerli bir sayısal ID girin.")
            return

        record = self.database.get_record_by_id(int(record_id))
        if not record:
            print("Kayıt bulunamadı.")
            return

        print(f"\nID: {record['id']}")
        print(f"Dosya Adı: {record['dosya_adi']}")
        print(f"Oluşturma: {record['olusturma_tarihi']}")
        print("\n--- DEŞİFRE ---")
        print(record['metin_icerigi'])
        print("\n--- ÖZET ---")
        print(record['ozet_metni'])

    def delete_record(self):
        record_id = input("Silinecek kayıt ID'si: ").strip()
        if not record_id.isdigit():
            print("Lütfen geçerli bir sayısal ID girin.")
            return

        record = self.database.get_record_by_id(int(record_id))
        if not record:
            print("Kayıt bulunamadı.")
            return

        confirm = input(f"[{record['id']}] {record['dosya_adi']} kaydını silmek istediğinize emin misiniz? (e/h): ").strip().lower()
        if confirm != "e":
            print("Silme işlemi iptal edildi.")
            return

        cursor = self.database.connection.cursor()
        cursor.execute("DELETE FROM kayitlar WHERE id = ?", (int(record_id),))
        self.database.connection.commit()
        print("Kayıt silindi.")

    def _analyze_text_safe(self, text):
        try:
            return self.engine.analyze_text(text)
        except Exception as exc:
            print(f"Analiz yapılamadı: {exc}")
            return "[Özetleme yapılamadı]"


def main():
    ensure_environment()
    load_environment()

    api_key = os.environ.get("GROQ_API_KEY")
    engine = VNSEngine(groq_api_key=api_key)
    database = Database(DB_PATH)

    print("\nVNS uygulaması başlıyor...")
    if not engine.can_transcribe():
        print("Not: faster-whisper yüklü değil, ses dosyası transkripsiyonu yapılamayabilir.")
    if not engine.can_analyze():
        print("Not: Groq analizi yapılamıyor. GROQ_API_KEY veya groq paketi eksik olabilir.")

    ui = ConsoleUI(engine, database)
    ui.run()
    database.close()


if __name__ == "__main__":
    main()

