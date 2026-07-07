from database import veritabani_baglan


def butce_belirle(kullanici_id):
    aylik_limit = float(input("Aylik butce limiti giriniz: "))

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute(
        "SELECT id FROM butceler WHERE kullanici_id = ?",
        (kullanici_id,)
    )

    mevcut = imlec.fetchone()

    if mevcut:
        imlec.execute(
            "UPDATE butceler SET aylik_limit = ? WHERE kullanici_id = ?",
            (aylik_limit, kullanici_id)
        )
        print("\n✅ Butce limiti guncellendi.")
    else:
        imlec.execute(
            "INSERT INTO butceler (kullanici_id, aylik_limit) VALUES (?, ?)",
            (kullanici_id, aylik_limit)
        )
        print("\n✅ Butce limiti belirlendi.")

    baglanti.commit()
    baglanti.close()

def butce_uyarisi(kullanici_id):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute(
        "SELECT aylik_limit FROM butceler WHERE kullanici_id = ?",
        (kullanici_id,)
    )
    butce = imlec.fetchone()

    if not butce:
        baglanti.close()
        print("\n⚠️ Henüz bütçe limiti belirlenmemiş.")
        return

    aylik_limit = butce[0]

    imlec.execute(
        "SELECT SUM(tutar) FROM giderler WHERE kullanici_id = ?",
        (kullanici_id,)
    )
    toplam_gider = imlec.fetchone()[0] or 0

    baglanti.close()

    oran = (toplam_gider / aylik_limit) * 100

    print("\n===== BUTCE DURUMU =====")
    print(f"Aylık Bütçe Limiti: {aylik_limit:.2f} TL")
    print(f"Toplam Gider: {toplam_gider:.2f} TL")
    print(f"Kullanım Oranı: %{oran:.2f}")

    if toplam_gider > aylik_limit:
        print("❌ Bütçenizi aştınız!")
    elif oran >= 90:
        print("⚠️ Dikkat! Bütçenizin %90'ına ulaştınız.")
    else:
        print("✅ Bütçeniz kontrol altında.")