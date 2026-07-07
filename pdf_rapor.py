from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from database import veritabani_baglan


def pdf_rapor_olustur(kullanici_id):
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

    bakiye = toplam_gelir - toplam_gider
    baglanti.close()

    dosya_adi = "finans_raporu.pdf"

    pdf = canvas.Canvas(dosya_adi, pagesize=A4)
    pdf.setTitle("Finans Raporu")

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(180, 800, "Finans Raporu")

    pdf.setFont("Helvetica", 14)
    pdf.drawString(100, 720, f"Toplam Gelir: {toplam_gelir:.2f} TL")
    pdf.drawString(100, 690, f"Toplam Gider: {toplam_gider:.2f} TL")
    pdf.drawString(100, 660, f"Bakiye: {bakiye:.2f} TL")

    pdf.save()

    return dosya_adi