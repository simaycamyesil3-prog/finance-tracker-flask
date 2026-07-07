from database import veritabani_baglan,kayit_var_mi
from utils import sayi_al, tarih_al, kategori_sec, GELIR_KATEGORILERI


def gelir_ekle(kullanici_id):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    tutar = sayi_al("Gelir tutarı: ")
    kategori = kategori_sec(GELIR_KATEGORILERI)
    aciklama = input("Açıklama: ")
    tarih = tarih_al()

    imlec.execute("""
INSERT INTO gelirler
(tutar, kategori, aciklama, tarih, kullanici_id)
VALUES (?, ?, ?, ?, ?)
""", (tutar, kategori, aciklama, tarih, kullanici_id))
    

    baglanti.commit()
    baglanti.close()

    print("\n✅ Gelir başarıyla eklendi.")


def gelirleri_listele(kullanici_id):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute(
    "SELECT * FROM gelirler WHERE kullanici_id = ? ORDER BY id DESC",
    (kullanici_id,)
)
    gelirler = imlec.fetchall()

    baglanti.close()

    print("\n===== GELİRLER =====")

    if not gelirler:
        print("Henüz gelir kaydı bulunmuyor.")
        return

    for gelir in gelirler:
        print(
            f"ID: {gelir[0]} | "
            f"{gelir[1]:.2f} TL | "
            f"{gelir[2]} | "
            f"{gelir[3]} | "
            f"{gelir[4]}"
        )


def gelir_sil():
    gelirleri_listele()

    try:
        kayit_id = int(input("\nSilinecek gelir ID: "))
    except ValueError:
        print("Geçersiz ID.")
        return

    if not kayit_var_mi("gelirler", kayit_id):
        print("Bu ID bulunamadı.")
        return

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("DELETE FROM gelirler WHERE id = ?", (kayit_id,))

    baglanti.commit()
    baglanti.close()

    print("✅ Gelir silindi.")


def gelir_guncelle():
    gelirleri_listele()

    try:
        kayit_id = int(input("\nGüncellenecek gelir ID: "))
    except ValueError:
        print("Geçersiz ID.")
        return

    if not kayit_var_mi("gelirler", kayit_id):
        print("Bu ID bulunamadı.")
        return

    tutar = sayi_al("Yeni tutar: ")
    kategori = kategori_sec(GELIR_KATEGORILERI)
    aciklama = input("Yeni açıklama: ")
    tarih = tarih_al()

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        UPDATE gelirler
        SET tutar = ?, kategori = ?, aciklama = ?, tarih = ?
        WHERE id = ?
    """, (tutar, kategori, aciklama, tarih, kayit_id))

    baglanti.commit()
    baglanti.close()

    print("✅ Gelir güncellendi.")