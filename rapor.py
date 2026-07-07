import csv
from database import veritabani_baglan


def finans_ozeti(kullanici_id):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("SELECT SUM(tutar) FROM gelirler WHERE kullanici_id = ?", (kullanici_id,))
    toplam_gelir = imlec.fetchone()[0] or 0

    imlec.execute("SELECT SUM(tutar) FROM giderler WHERE kullanici_id = ?", (kullanici_id,))
    toplam_gider = imlec.fetchone()[0] or 0

    baglanti.close()

    bakiye = toplam_gelir - toplam_gider

    print("\n===== FINANS OZETI =====")
    print(f"Toplam Gelir: {toplam_gelir:.2f} TL")
    print(f"Toplam Gider: {toplam_gider:.2f} TL")
    print(f"Bakiye: {bakiye:.2f} TL")


def istatistikler(kullanici_id):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute(
        "SELECT COUNT(*), SUM(tutar), AVG(tutar), MAX(tutar) FROM gelirler WHERE kullanici_id = ?",
        (kullanici_id,)
    )
    gelir = imlec.fetchone()

    imlec.execute(
        "SELECT COUNT(*), SUM(tutar), AVG(tutar), MAX(tutar) FROM giderler WHERE kullanici_id = ?",
        (kullanici_id,)
    )
    gider = imlec.fetchone()

    baglanti.close()

    print("\n===== ISTATISTIKLER =====")
    print(f"Gelir islem sayisi: {gelir[0]}")
    print(f"Toplam gelir: {(gelir[1] or 0):.2f} TL")
    print(f"Ortalama gelir: {(gelir[2] or 0):.2f} TL")
    print(f"En yuksek gelir: {(gelir[3] or 0):.2f} TL")

    print("-" * 30)

    print(f"Gider islem sayisi: {gider[0]}")
    print(f"Toplam gider: {(gider[1] or 0):.2f} TL")
    print(f"Ortalama gider: {(gider[2] or 0):.2f} TL")
    print(f"En yuksek gider: {(gider[3] or 0):.2f} TL")


def kategori_analizi(kullanici_id):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT kategori, SUM(tutar) as toplam
        FROM giderler
        WHERE kullanici_id = ?
        GROUP BY kategori
        ORDER BY toplam DESC
    """, (kullanici_id,))

    sonuclar = imlec.fetchall()
    baglanti.close()

    print("\n===== KATEGORI BAZLI GIDER ANALIZI =====")

    if not sonuclar:
        print("Henuz gider kaydi bulunmuyor.")
        return

    for kategori, toplam in sonuclar:
        print(f"{kategori}: {toplam:.2f} TL")

    print(f"\nEn cok harcama yapilan kategori: {sonuclar[0][0]} ({sonuclar[0][1]:.2f} TL)")

def arama_yap(kullanici_id):
    kelime = input("Aranacak kelime/kategori/tarih: ")

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    print("\n===== GELIR ARAMA SONUCLARI =====")

    imlec.execute("""
        SELECT *
        FROM gelirler
        WHERE kullanici_id = ?
        AND (kategori LIKE ? OR aciklama LIKE ? OR tarih LIKE ?)
    """, (kullanici_id, f"%{kelime}%", f"%{kelime}%", f"%{kelime}%"))

    gelirler = imlec.fetchall()

    if not gelirler:
        print("Gelirlerde sonuc bulunamadi.")
    else:
        for gelir in gelirler:
            print(f"ID: {gelir[0]} | {gelir[1]:.2f} TL | {gelir[2]} | {gelir[3]} | {gelir[4]}")

    print("\n===== GIDER ARAMA SONUCLARI =====")

    imlec.execute("""
        SELECT *
        FROM giderler
        WHERE kullanici_id = ?
        AND (kategori LIKE ? OR aciklama LIKE ? OR tarih LIKE ?)
    """, (kullanici_id, f"%{kelime}%", f"%{kelime}%", f"%{kelime}%"))

    giderler = imlec.fetchall()
    baglanti.close()

    if not giderler:
        print("Giderlerde sonuc bulunamadi.")
    else:
        for gider in giderler:
            print(f"ID: {gider[0]} | {gider[1]:.2f} TL | {gider[2]} | {gider[3]} | {gider[4]}")

def csv_disari_aktar(kullanici_id):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute(
        "SELECT id, tutar, kategori, aciklama, tarih FROM gelirler WHERE kullanici_id = ?",
        (kullanici_id,)
    )
    gelirler = imlec.fetchall()

    with open("gelirler.csv", "w", newline="", encoding="utf-8") as dosya:
        yazici = csv.writer(dosya)
        yazici.writerow(["ID", "Tutar", "Kategori", "Aciklama", "Tarih"])
        yazici.writerows(gelirler)

    imlec.execute(
        "SELECT id, tutar, kategori, aciklama, tarih FROM giderler WHERE kullanici_id = ?",
        (kullanici_id,)
    )
    giderler = imlec.fetchall()

    with open("giderler.csv", "w", newline="", encoding="utf-8") as dosya:
        yazici = csv.writer(dosya)
        yazici.writerow(["ID", "Tutar", "Kategori", "Aciklama", "Tarih"])
        yazici.writerows(giderler)

    baglanti.close()

    print("Veriler CSV dosyalarina aktarildi.")
    print("Olusturulan dosyalar: gelirler.csv ve giderler.csv")


def son_10_islem(kullanici_id):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT 'Gelir' as tur, tutar, kategori, aciklama, tarih
        FROM gelirler
        WHERE kullanici_id = ?

        UNION ALL

        SELECT 'Gider' as tur, tutar, kategori, aciklama, tarih
        FROM giderler
        WHERE kullanici_id = ?

        ORDER BY tarih DESC, tur ASC
        LIMIT 10
    """, (kullanici_id, kullanici_id))

    islemler = imlec.fetchall()
    baglanti.close()

    print("\n===== SON 10 ISLEM =====")

    if not islemler:
        print("Henuz kayit bulunmuyor.")
        return

    for islem in islemler:
        print(f"{islem[0]} | {islem[1]:.2f} TL | {islem[2]} | {islem[3]} | {islem[4]}")

def aylik_rapor(kullanici_id):
    ay = input("Ay giriniz (01-12): ")
    yil = input("Yil giriniz (YYYY): ")

    tarih_arama = f"%.{ay}.{yil}"

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT SUM(tutar)
        FROM gelirler
        WHERE kullanici_id = ?
        AND tarih LIKE ?
    """, (kullanici_id, tarih_arama))

    toplam_gelir = imlec.fetchone()[0] or 0

    imlec.execute("""
        SELECT SUM(tutar)
        FROM giderler
        WHERE kullanici_id = ?
        AND tarih LIKE ?
    """, (kullanici_id, tarih_arama))

    toplam_gider = imlec.fetchone()[0] or 0

    baglanti.close()

    bakiye = toplam_gelir - toplam_gider

    print(f"\n===== {ay}.{yil} AYLIK RAPOR =====")
    print(f"Toplam Gelir: {toplam_gelir:.2f} TL")
    print(f"Toplam Gider: {toplam_gider:.2f} TL")
    print(f"Bakiye: {bakiye:.2f} TL")