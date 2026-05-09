import sqlite3
import os
from datetime import datetime

# Klasör ve veritabanı yolu
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "vns.db")

def connect_db():
    # Eğer "data" klasörü yoksa hata almamak için oluşturuyoruz
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Hatalı Türkçe SQL komutu düzeltildi
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kayitlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dosya_adi TEXT,
        metin_icerigi TEXT,
        ozet_metni TEXT,
        olusturma_tarihi TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_record(dosya_adi, metin_icerigi, ozet_metni):
    conn = connect_db()
    cursor = conn.cursor()

    # Tarihi UI'da okunaklı olsun diye string formatına çevirdik
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO kayitlar (dosya_adi, metin_icerigi, ozet_metni, olusturma_tarihi)
    VALUES (?, ?, ?, ?)
    """, (dosya_adi, metin_icerigi, ozet_metni, tarih))

    conn.commit()
    conn.close()


def get_all_records():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM kayitlar ORDER BY olusturma_tarihi DESC")
    data = cursor.fetchall()

    conn.close()
    return data


def get_record_by_id(kayit_id):
    conn = connect_db()
    cursor = conn.cursor()

    # Tablo adı "records" yerine "kayitlar" olarak düzeltildi
    cursor.execute("SELECT * FROM kayitlar WHERE id = ?", (kayit_id,))
    data = cursor.fetchone()        

    conn.close()
    return data


def delete_record(kayit_id):
    conn = connect_db()
    cursor = conn.cursor()

    # Tablo adı "records" yerine "kayitlar" olarak düzeltildi
    cursor.execute("DELETE FROM kayitlar WHERE id = ?", (kayit_id,))

    conn.commit()
    conn.close()


def search_records(anahtar_kelime):
    conn = connect_db()
    cursor = conn.cursor()

    # Tablo adı ve Sütun adları düzeltildi
    cursor.execute("""
    SELECT * FROM kayitlar
    WHERE metin_icerigi LIKE ? OR ozet_metni LIKE ?
    """, (f"%{anahtar_kelime}%", f"%{anahtar_kelime}%"))

    data = cursor.fetchall()

    conn.close()
    return data
    
# Dosya direkt çalıştırılırsa veritabanını test edip tabloları oluştursun
if __name__ == "__main__":
    create_tables()
    print("[Sistem] Veritabanı ve tablolar başarıyla kontrol edildi/oluşturuldu.")