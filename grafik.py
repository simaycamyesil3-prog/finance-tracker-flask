import matplotlib.pyplot as plt
from database import veritabani_baglan


def gelir_gider_grafigi(kullanici_id):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute(
        "SELECT SUM(tutar) FROM gelirler WHERE kullanici_id = ?",
        (kullanici_id,)
    )
    toplam_gelir = imlec.fetchone()[0] or 0

    imlec.execute(
        "SELECT SUM(tutar) FROM giderler WHERE kullanici_id = ?",
        (kullanici_id,)
    )
    toplam_gider = imlec.fetchone()[0] or 0

    baglanti.close()

    etiketler = ["Gelir", "Gider"]
    degerler = [toplam_gelir, toplam_gider]

    plt.figure(figsize=(6, 5))
    plt.bar(etiketler, degerler)
    plt.title("Gelir - Gider Grafiği")
    plt.ylabel("TL")
    plt.show()
