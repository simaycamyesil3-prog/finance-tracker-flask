import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "finans.db")


def veritabani_baglan():
    return sqlite3.connect(DB_NAME)


def tablolari_olustur():
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
    CREATE TABLE IF NOT EXISTS gelirler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tutar REAL NOT NULL,
        kategori TEXT NOT NULL,
        aciklama TEXT NOT NULL,
        tarih TEXT NOT NULL,
        kullanici_id INTEGER
    )
    """)

    imlec.execute("""
    CREATE TABLE IF NOT EXISTS giderler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tutar REAL NOT NULL,
        kategori TEXT NOT NULL,
        aciklama TEXT NOT NULL,
        tarih TEXT NOT NULL,
        kullanici_id INTEGER
    )
    """)

    imlec.execute("""
    CREATE TABLE IF NOT EXISTS kullanicilar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad_soyad TEXT NOT NULL,
    kullanici_adi TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    sifre TEXT NOT NULL,
    olusturma_tarihi TEXT NOT NULL
)
""")
    
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS butceler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kullanici_id INTEGER NOT NULL,
    aylik_limit REAL NOT NULL
)
""")
    
    try:
        imlec.execute("ALTER TABLE gelirler ADD COLUMN kullanici_id INTEGER")
    except sqlite3.OperationalError:
        pass

    try:
        imlec.execute("ALTER TABLE giderler ADD COLUMN kullanici_id INTEGER")
    except sqlite3.OperationalError:
        pass

    baglanti.commit()
    baglanti.close()


def kayit_var_mi(tablo: str, kayit_id: int):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute(f"SELECT id FROM {tablo} WHERE id = ?", (kayit_id,))
    sonuc = imlec.fetchone()

    baglanti.close()
    return sonuc is not None