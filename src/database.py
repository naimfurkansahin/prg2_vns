import sqlite3
from datetime import datetime


DB_PATH="data/vns.db"

def connect_db():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute("""
    EGER BU İSİMDE BİR TABLO YOKSA OLUSTUR kayitlar (
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

    cursor.execute("""
    INSERT INTO kayitlar (dosya_adi, metin_icerigi, ozet_metni, olusturma_tarihi)
    VALUES (?, ?, ?, ?)
    """, (dosya_adi, metin_icerigi, ozet_metni, datetime.now()))

    conn.commit()
    conn.close()


def get_all_records():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM kayitlar ORDER BY olusturma_tarihi DESC")
    data = cursor.fetchall()

    conn.close()
    return data
