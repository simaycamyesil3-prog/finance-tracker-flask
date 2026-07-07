from database import veritabani_baglan
from datetime import datetime
import hashlib


def sifre_hashle(sifre): # type: ignore
    return hashlib.sha256(sifre.encode()).hexdigest() # type: ignore


def kayit_ol():
    ad_soyad = input("Ad Soyad: ")
    kullanici_adi = input("Kullanıcı Adı: ")
    email = input("Email: ")
    sifre = input("Şifre: ")

    sifreli = sifre_hashle(sifre)
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    try:
        imlec.execute("""
        INSERT INTO kullanicilar
        (ad_soyad, kullanici_adi, email, sifre, olusturma_tarihi)
        VALUES (?, ?, ?, ?, ?)
        """, (ad_soyad, kullanici_adi, email, sifreli, tarih))

        baglanti.commit()
        print("\n✅ Kayıt başarıyla oluşturuldu.")
    except Exception:
        print("\n❌ Bu kullanıcı adı veya email zaten kayıtlı.")
    finally:
        baglanti.close()

def giris_yap():
    kullanici_adi = input("Kullanıcı Adı: ")
    sifre = input("Şifre: ")

    sifreli = sifre_hashle(sifre)

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
    SELECT id, ad_soyad
     FROM kullanicilar
     WHERE kullanici_adi=? AND sifre=?
    """, (kullanici_adi, sifreli))

    kullanici = imlec.fetchone()

    baglanti.close()

    if kullanici:
       print(f"\n✅ Hoş geldiniz {kullanici[1]}!")
       return kullanici[0]
    else:
       print("\n❌ Kullanıcı adı veya şifre yanlış.")
       return None
     