import time
import re

from flask import Flask, render_template, request, redirect, session, send_file
from database import veritabani_baglan, tablolari_olustur
from datetime import datetime
from functools import wraps

from pdf_rapor import pdf_rapor_olustur
from excel_rapor import excel_rapor_olustur
from auth import sifre_hashle
from mail_service import mail_ayarlari, kod_uret, mail_gonder


app = Flask(__name__)
app.secret_key = "finans_takip_gizli_anahtar"

mail_ayarlari(app)
tablolari_olustur()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "kullanici_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def sifre_guclu_mu(sifre):
    if len(sifre) < 8:
        return False
    if not re.search(r"[A-Z]", sifre):
        return False
    if not re.search(r"[a-z]", sifre):
        return False
    if not re.search(r"[0-9]", sifre):
        return False
    return True


@app.route("/")
def ana_sayfa():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "kullanici_id" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        kullanici_adi = request.form["kullanici_adi"]
        sifre = request.form["sifre"]
        sifreli = sifre_hashle(sifre)

        baglanti = veritabani_baglan()
        imlec = baglanti.cursor()

        imlec.execute("""
            SELECT id, ad_soyad
            FROM kullanicilar
            WHERE (kullanici_adi = ? OR email = ?)
            AND (sifre = ? OR sifre = ?)
        """, (kullanici_adi, kullanici_adi, sifreli, sifre))

        kullanici = imlec.fetchone()
        baglanti.close()

        if kullanici:
            session["kullanici_id"] = kullanici[0]
            session["ad_soyad"] = kullanici[1]
            return redirect("/dashboard")

        return "Kullanıcı adı veya şifre yanlış."

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "kullanici_id" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        ad_soyad = request.form["ad_soyad"]
        kullanici_adi = request.form["kullanici_adi"]
        email = request.form["email"]
        sifre = request.form["sifre"]

        if not sifre_guclu_mu(sifre):
            return "Şifre en az 8 karakter, 1 büyük harf, 1 küçük harf ve 1 rakam içermelidir."

        baglanti = veritabani_baglan()
        imlec = baglanti.cursor()

        imlec.execute("""
            SELECT id FROM kullanicilar
            WHERE kullanici_adi = ? OR email = ?
        """, (kullanici_adi, email))

        mevcut = imlec.fetchone()
        baglanti.close()

        if mevcut:
            return "Bu kullanıcı adı veya e-posta zaten kayıtlı."

        kod = kod_uret()

        session["kayit_bilgileri"] = {
            "ad_soyad": ad_soyad,
            "kullanici_adi": kullanici_adi,
            "email": email,
            "sifre": sifre_hashle(sifre),
            "kod": kod,
            "zaman": time.time()
        }

        mail_durumu = mail_gonder(
            email,
            "Finans Takip - E-posta Doğrulama Kodu",
            f"Merhaba {ad_soyad},\n\nDoğrulama kodunuz: {kod}\n\nBu kod 10 dakika geçerlidir."
        )

        if not mail_durumu:
            return "Mail gönderilemedi. Render MAIL_USERNAME ve MAIL_PASSWORD ayarlarını kontrol et."

        return redirect("/kod-dogrula")

    return render_template("register.html")


@app.route("/kod-dogrula", methods=["GET", "POST"])
def kod_dogrula():
    if "kayit_bilgileri" not in session:
        return redirect("/register")

    bilgiler = session["kayit_bilgileri"]

    if time.time() - bilgiler["zaman"] > 600:
        session.pop("kayit_bilgileri", None)
        return "Kodun süresi doldu. Lütfen tekrar kayıt olun."

    if request.method == "POST":
        girilen_kod = request.form["kod"]

        if girilen_kod != bilgiler["kod"]:
            return "Doğrulama kodu yanlış."

        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        baglanti = veritabani_baglan()
        imlec = baglanti.cursor()

        try:
            imlec.execute("""
                INSERT INTO kullanicilar
                (ad_soyad, kullanici_adi, email, sifre, olusturma_tarihi)
                VALUES (?, ?, ?, ?, ?)
            """, (
                bilgiler["ad_soyad"],
                bilgiler["kullanici_adi"],
                bilgiler["email"],
                bilgiler["sifre"],
                tarih
            ))

            baglanti.commit()
            session.pop("kayit_bilgileri", None)
            return redirect("/login")

        except Exception as e:
            return f"Kayıt hatası: {e}"

        finally:
            baglanti.close()

    return render_template("kod_dogrula.html")


@app.route("/sifremi-unuttum", methods=["GET", "POST"])
def sifremi_unuttum():
    if request.method == "POST":
        email = request.form["email"]

        baglanti = veritabani_baglan()
        imlec = baglanti.cursor()

        imlec.execute("SELECT id, ad_soyad FROM kullanicilar WHERE email = ?", (email,))
        kullanici = imlec.fetchone()
        baglanti.close()

        if not kullanici:
            return "Bu e-posta adresiyle kayıtlı kullanıcı bulunamadı."

        kod = kod_uret()

        session["sifre_sifirlama"] = {
            "email": email,
            "kod": kod,
            "zaman": time.time()
        }

        mail_durumu = mail_gonder(
            email,
            "Finans Takip - Şifre Sıfırlama Kodu",
            f"Merhaba {kullanici[1]},\n\nŞifre sıfırlama kodunuz: {kod}\n\nBu kod 10 dakika geçerlidir."
        )

        if not mail_durumu:
            return "Mail gönderilemedi. Render MAIL_USERNAME ve MAIL_PASSWORD ayarlarını kontrol et."

        return redirect("/sifre-kod-dogrula")

    return render_template("sifremi_unuttum.html")


@app.route("/sifre-kod-dogrula", methods=["GET", "POST"])
def sifre_kod_dogrula():
    if "sifre_sifirlama" not in session:
        return redirect("/sifremi-unuttum")

    bilgiler = session["sifre_sifirlama"]

    if time.time() - bilgiler["zaman"] > 600:
        session.pop("sifre_sifirlama", None)
        return "Kodun süresi doldu. Lütfen tekrar deneyin."

    if request.method == "POST":
        girilen_kod = request.form["kod"]

        if girilen_kod != bilgiler["kod"]:
            return "Kod yanlış."

        session["sifre_kodu_onaylandi"] = True
        return redirect("/sifre-sifirla")

    return render_template("kod_dogrula.html")


@app.route("/sifre-sifirla", methods=["GET", "POST"])
def sifre_sifirla():
    if "sifre_sifirlama" not in session or not session.get("sifre_kodu_onaylandi"):
        return redirect("/sifremi-unuttum")

    if request.method == "POST":
        yeni_sifre = request.form["yeni_sifre"]
        yeni_sifre_tekrar = request.form["yeni_sifre_tekrar"]

        if yeni_sifre != yeni_sifre_tekrar:
            return "Şifreler eşleşmiyor."

        if not sifre_guclu_mu(yeni_sifre):
            return "Şifre en az 8 karakter, 1 büyük harf, 1 küçük harf ve 1 rakam içermelidir."

        sifreli = sifre_hashle(yeni_sifre)
        email = session["sifre_sifirlama"]["email"]

        baglanti = veritabani_baglan()
        imlec = baglanti.cursor()

        imlec.execute("""
            UPDATE kullanicilar
            SET sifre = ?
            WHERE email = ?
        """, (sifreli, email))

        baglanti.commit()
        baglanti.close()

        session.pop("sifre_sifirlama", None)
        session.pop("sifre_kodu_onaylandi", None)

        return redirect("/login")

    return render_template("sifre_sifirla.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/dashboard")
@login_required
def dashboard():
    kullanici_id = session["kullanici_id"]

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    # Toplam gelir
    imlec.execute(
        "SELECT SUM(tutar) FROM gelirler WHERE kullanici_id = ?",
        (kullanici_id,)
    )
    toplam_gelir = imlec.fetchone()[0] or 0

    # Toplam gider
    imlec.execute(
        "SELECT SUM(tutar) FROM giderler WHERE kullanici_id = ?",
        (kullanici_id,)
    )
    toplam_gider = imlec.fetchone()[0] or 0

    bakiye = toplam_gelir - toplam_gider

    # Son 5 işlem
    imlec.execute("""
        SELECT 'Gelir' AS tur, tutar, kategori, aciklama, tarih
        FROM gelirler
        WHERE kullanici_id = ?

        UNION ALL

        SELECT 'Gider' AS tur, tutar, kategori, aciklama, tarih
        FROM giderler
        WHERE kullanici_id = ?

        ORDER BY tarih DESC
        LIMIT 5
    """, (kullanici_id, kullanici_id))

    son_islemler = imlec.fetchall()

    # Gider kategorileri
    imlec.execute("""
        SELECT kategori, SUM(tutar)
        FROM giderler
        WHERE kullanici_id = ?
        GROUP BY kategori
        ORDER BY SUM(tutar) DESC
    """, (kullanici_id,))

    kategori_verileri = imlec.fetchall()

    kategori_etiketleri = [satir[0] for satir in kategori_verileri]
    kategori_tutarlari = [float(satir[1]) for satir in kategori_verileri]

    # Son 6 ayı oluştur
    ay_isimleri = [
        "Oca", "Şub", "Mar", "Nis", "May", "Haz",
        "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"
    ]

    simdi = datetime.now()
    son_alti_ay = []

    for geriye in range(5, -1, -1):
        toplam_ay = simdi.year * 12 + simdi.month - 1 - geriye
        yil = toplam_ay // 12
        ay = toplam_ay % 12 + 1

        son_alti_ay.append({
            "anahtar": f"{yil}-{ay:02d}",
            "etiket": f"{ay_isimleri[ay - 1]} {str(yil)[-2:]}"
        })

    aylik_etiketler = [ay["etiket"] for ay in son_alti_ay]
    aylik_gelirler = []
    aylik_giderler = []

    for ay in son_alti_ay:
        ay_anahtari = ay["anahtar"]

        imlec.execute("""
            SELECT SUM(tutar)
            FROM gelirler
            WHERE kullanici_id = ?
            AND substr(tarih, 1, 7) = ?
        """, (kullanici_id, ay_anahtari))

        ay_geliri = imlec.fetchone()[0] or 0
        aylik_gelirler.append(float(ay_geliri))

        imlec.execute("""
            SELECT SUM(tutar)
            FROM giderler
            WHERE kullanici_id = ?
            AND substr(tarih, 1, 7) = ?
        """, (kullanici_id, ay_anahtari))

        ay_gideri = imlec.fetchone()[0] or 0
        aylik_giderler.append(float(ay_gideri))

    baglanti.close()

    return render_template(
        "dashboard.html",
        gelir=toplam_gelir,
        gider=toplam_gider,
        bakiye=bakiye,
        ad_soyad=session["ad_soyad"],
        son_islemler=son_islemler,
        kategori_etiketleri=kategori_etiketleri,
        kategori_tutarlari=kategori_tutarlari,
        aylik_etiketler=aylik_etiketler,
        aylik_gelirler=aylik_gelirler,
        aylik_giderler=aylik_giderler
    )

@app.route("/gelir-ekle", methods=["GET", "POST"])
@login_required
def web_gelir_ekle():
    if request.method == "POST":
        tutar = request.form["tutar"]
        kategori = request.form["kategori"]
        aciklama = request.form["aciklama"]
        tarih = request.form["tarih"]
        kullanici_id = session["kullanici_id"]

        baglanti = veritabani_baglan()
        imlec = baglanti.cursor()

        imlec.execute("""
            INSERT INTO gelirler (tutar, kategori, aciklama, tarih, kullanici_id)
            VALUES (?, ?, ?, ?, ?)
        """, (tutar, kategori, aciklama, tarih, kullanici_id))

        baglanti.commit()
        baglanti.close()

        return redirect("/dashboard")

    return render_template("gelir_ekle.html")


@app.route("/gider-ekle", methods=["GET", "POST"])
@login_required
def web_gider_ekle():
    if request.method == "POST":
        tutar = request.form["tutar"]
        kategori = request.form["kategori"]
        aciklama = request.form["aciklama"]
        tarih = request.form["tarih"]
        kullanici_id = session["kullanici_id"]

        baglanti = veritabani_baglan()
        imlec = baglanti.cursor()

        imlec.execute("""
            INSERT INTO giderler (tutar, kategori, aciklama, tarih, kullanici_id)
            VALUES (?, ?, ?, ?, ?)
        """, (tutar, kategori, aciklama, tarih, kullanici_id))

        baglanti.commit()
        baglanti.close()

        return redirect("/dashboard")

    return render_template("gider_ekle.html")


@app.route("/raporlar")
@login_required
def web_raporlar():
    kullanici_id = session["kullanici_id"]

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT id, 'Gelir' as tur, tutar, kategori, aciklama, tarih
        FROM gelirler
        WHERE kullanici_id = ?

        UNION ALL

        SELECT id, 'Gider' as tur, tutar, kategori, aciklama, tarih
        FROM giderler
        WHERE kullanici_id = ?

        ORDER BY tarih DESC
    """, (kullanici_id, kullanici_id))

    islemler = imlec.fetchall()

    imlec.execute("SELECT SUM(tutar) FROM gelirler WHERE kullanici_id = ?", (kullanici_id,))
    gelir = imlec.fetchone()[0] or 0

    imlec.execute("SELECT SUM(tutar) FROM giderler WHERE kullanici_id = ?", (kullanici_id,))
    gider = imlec.fetchone()[0] or 0

    baglanti.close()

    return render_template(
        "raporlar.html",
        islemler=islemler,
        gelir=gelir,
        gider=gider,
        bakiye=gelir - gider,
        ad_soyad=session["ad_soyad"]
    )


@app.route("/duzenle/<int:id>/<tur>", methods=["GET", "POST"])
@login_required
def duzenle(id, tur):
    kullanici_id = session["kullanici_id"]
    tablo = "gelirler" if tur == "Gelir" else "giderler"

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    if request.method == "POST":
        tutar = request.form["tutar"]
        kategori = request.form["kategori"]
        aciklama = request.form["aciklama"]
        tarih = request.form["tarih"]

        imlec.execute(f"""
            UPDATE {tablo}
            SET tutar=?, kategori=?, aciklama=?, tarih=?
            WHERE id=? AND kullanici_id=?
        """, (tutar, kategori, aciklama, tarih, id, kullanici_id))

        baglanti.commit()
        baglanti.close()

        return redirect("/raporlar")

    imlec.execute(f"SELECT * FROM {tablo} WHERE id=? AND kullanici_id=?", (id, kullanici_id))
    kayit = imlec.fetchone()

    baglanti.close()

    if not kayit:
        return redirect("/raporlar")

    return render_template("duzenle.html", kayit=kayit)


@app.route("/sil/<int:id>/<tur>")
@login_required
def sil(id, tur):
    kullanici_id = session["kullanici_id"]
    tablo = "gelirler" if tur == "Gelir" else "giderler"

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute(
        f"DELETE FROM {tablo} WHERE id = ? AND kullanici_id = ?",
        (id, kullanici_id)
    )

    baglanti.commit()
    baglanti.close()

    return redirect("/raporlar")


@app.route("/grafikler")
@login_required
def web_grafikler():
    kullanici_id = session["kullanici_id"]

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("SELECT SUM(tutar) FROM gelirler WHERE kullanici_id = ?", (kullanici_id,))
    gelir = imlec.fetchone()[0] or 0

    imlec.execute("SELECT SUM(tutar) FROM giderler WHERE kullanici_id = ?", (kullanici_id,))
    gider = imlec.fetchone()[0] or 0

    baglanti.close()

    return render_template("grafikler.html", gelir=gelir, gider=gider)


@app.route("/pdf-indir")
@login_required
def pdf_indir():
    kullanici_id = session["kullanici_id"]
    dosya_adi = pdf_rapor_olustur(kullanici_id)

    return send_file(dosya_adi, as_attachment=True)


@app.route("/excel-indir")
@login_required
def excel_indir():
    kullanici_id = session["kullanici_id"]
    dosya_adi = excel_rapor_olustur(kullanici_id)

    return send_file(dosya_adi, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)