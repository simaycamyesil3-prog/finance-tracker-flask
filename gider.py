from database import veritabani_baglan, kayit_var_mi
from utils import sayi_al, tarih_al, kategori_sec, GIDER_KATEGORILERI


def gider_ekle(kullanici_id):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    tutar = sayi_al("Gider tutari: ")
    kategori = kategori_sec(GIDER_KATEGORILERI)
    aciklama = input("Aciklama: ")
    tarih = tarih_al()

    imlec.execute("""
        INSERT INTO giderler (tutar, kategori, aciklama, tarih,kullanici_id)
        VALUES (?, ?, ?, ?)
    """, (tutar, kategori, aciklama, tarih,kullanici_id))

    baglanti.commit()
    baglanti.close()

    print("\nGider basariyla eklendi.")


def giderleri_listele(kullanici_id):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute(
        "SELECT * FROM giderler WHERE kullanici_id = ? ORDER BY id DESC",
        (kullanici_id,)
    )
    giderler = imlec.fetchall()

    baglanti.close()

    print("\n===== GIDERLER =====")

    if not giderler:
        print("Henuz gider kaydi bulunmuyor.")
        return

    for gider in giderler:
        print(
            f"ID: {gider[0]} | "
            f"{gider[1]:.2f} TL | "
            f"{gider[2]} | "
            f"{gider[3]} | "
            f"{gider[4]}"
        )


def gider_sil():
    giderleri_listele()

    try:
        kayit_id = int(input("\nSilinecek gider ID: "))
    except ValueError:
        print("Gecersiz ID.")
        return

    if not kayit_var_mi("giderler", kayit_id):
        print("Bu ID bulunamadi.")
        return

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("DELETE FROM giderler WHERE id = ?", (kayit_id,))

    baglanti.commit()
    baglanti.close()

    print("Gider silindi.")


def gider_guncelle():
    giderleri_listele()

    try:
        kayit_id = int(input("\nGuncellenecek gider ID: "))
    except ValueError:
        print("Gecersiz ID.")
        return

    if not kayit_var_mi("giderler", kayit_id):
        print("Bu ID bulunamadi.")
        return

    tutar = sayi_al("Yeni tutar: ")
    kategori = kategori_sec(GIDER_KATEGORILERI)
    aciklama = input("Yeni aciklama: ")
    tarih = tarih_al()

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        UPDATE giderler
        SET tutar = ?, kategori = ?, aciklama = ?, tarih = ?
        WHERE id = ?
    """, (tutar, kategori, aciklama, tarih, kayit_id))

    baglanti.commit()
    baglanti.close()

    print("Gider guncellendi.")