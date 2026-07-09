from flask import Flask, render_template, request, redirect, session, send_file
from database import veritabani_baglan, tablolari_olustur
from datetime import datetime
from functools import wraps

from pdf_rapor import pdf_rapor_olustur
from excel_rapor import excel_rapor_olustur
from auth import sifre_hashle


app = Flask(__name__)
app.secret_key = "finans_takip_gizli_anahtar"

tablolari_olustur()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "kullanici_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


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
            return redirect("/login")

        except Exception as e:
            return f"Kayıt hatası: {e}"

        finally:
            baglanti.close()

    return render_template("register.html")


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

    imlec.execute("SELECT SUM(tutar) FROM gelirler WHERE kullanici_id = ?", (kullanici_id,))
    toplam_gelir = imlec.fetchone()[0] or 0

    imlec.execute("SELECT SUM(tutar) FROM giderler WHERE kullanici_id = ?", (kullanici_id,))
    toplam_gider = imlec.fetchone()[0] or 0

    bakiye = toplam_gelir - toplam_gider

    imlec.execute("""
        SELECT 'Gelir' as tur, tutar, kategori, aciklama, tarih
        FROM gelirler
        WHERE kullanici_id = ?

        UNION ALL

        SELECT 'Gider' as tur, tutar, kategori, aciklama, tarih
        FROM giderler
        WHERE kullanici_id = ?

        ORDER BY tarih DESC
        LIMIT 5
    """, (kullanici_id, kullanici_id))

    son_islemler = imlec.fetchall()

    imlec.execute("""
        SELECT kategori, SUM(tutar)
        FROM giderler
        WHERE kullanici_id = ?
        GROUP BY kategori
    """, (kullanici_id,))

    kategori_verileri = imlec.fetchall()
    baglanti.close()

    return render_template(
        "dashboard.html",
        gelir=toplam_gelir,
        gider=toplam_gider,
        bakiye=bakiye,
        ad_soyad=session["ad_soyad"],
        son_islemler=son_islemler,
        kategori_verileri=kategori_verileri
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
