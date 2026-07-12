import os
import random
import smtplib
from email.mime.text import MIMEText


def mail_ayarlari(app):
    # app.py içindeki mevcut çağrıyla uyumluluk için bırakıyoruz.
    pass


def kod_uret():
    return str(random.randint(100000, 999999))


def mail_gonder(alici, konu, icerik):
    mail_adresi = os.environ.get("MAIL_USERNAME")
    mail_sifresi = os.environ.get("MAIL_PASSWORD")

    if not mail_adresi or not mail_sifresi:
        print("MAIL_USERNAME veya MAIL_PASSWORD eksik.")
        return False

    mesaj = MIMEText(icerik, "plain", "utf-8")
    mesaj["Subject"] = konu
    mesaj["From"] = mail_adresi
    mesaj["To"] = alici

    server = None

    try:
        server = smtplib.SMTP(
            host="smtp.gmail.com",
            port=587,
            timeout=10
        )

        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(mail_adresi, mail_sifresi)
        server.sendmail(
            mail_adresi,
            [alici],
            mesaj.as_string()
        )

        print(f"Mail başarıyla gönderildi: {alici}")
        return True

    except smtplib.SMTPAuthenticationError as hata:
        print("Gmail giriş doğrulama hatası:", hata)
        return False

    except (TimeoutError, OSError, smtplib.SMTPException) as hata:
        print("SMTP bağlantı veya gönderme hatası:", hata)
        return False

    except Exception as hata:
        print("Beklenmeyen mail gönderme hatası:", hata)
        return False

    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass