import os
import random
import smtplib
from email.mime.text import MIMEText


def mail_ayarlari(app):
    pass


def kod_uret():
    return str(random.randint(100000, 999999))


def mail_gonder(alici, konu, icerik):
    try:
        mail_adresi = os.environ.get("MAIL_USERNAME")
        mail_sifresi = os.environ.get("MAIL_PASSWORD")

        if not mail_adresi or not mail_sifresi:
            print("MAIL_USERNAME veya MAIL_PASSWORD eksik.")
            return False

        mesaj = MIMEText(icerik, "plain", "utf-8")
        mesaj["Subject"] = konu
        mesaj["From"] = mail_adresi
        mesaj["To"] = alici

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=5)
        server.starttls()
        server.login(mail_adresi, mail_sifresi)
        server.sendmail(mail_adresi, [alici], mesaj.as_string())
        server.quit()

        return True

    except Exception as e:
        print("Mail gönderme hatası:", e)
        return False