from openpyxl import Workbook
from database import veritabani_baglan


def excel_rapor_olustur(kullanici_id):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT 'Gelir', tutar, kategori, aciklama, tarih
        FROM gelirler
        WHERE kullanici_id = ?

        UNION ALL

        SELECT 'Gider', tutar, kategori, aciklama, tarih
        FROM giderler
        WHERE kullanici_id = ?

        ORDER BY tarih DESC
    """, (kullanici_id, kullanici_id))

    islemler = imlec.fetchall()
    baglanti.close()

    dosya_adi = "finans_raporu.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Finans Raporu"

    ws.append(["Tür", "Tutar", "Kategori", "Açıklama", "Tarih"])

    for islem in islemler:
        ws.append(islem)

    wb.save(dosya_adi)

    return dosya_adi