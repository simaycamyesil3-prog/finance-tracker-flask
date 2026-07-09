import os
import random
import smtplib

from flask_mail import Mail, Message


mail = Mail()


def mail_ayarlari(app):
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True") == "True"
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_TIMEOUT"] = 5

    mail.init_app(app)


def kod_uret():
    return str(random.randint(100000, 999999))


def mail_gonder(alici, konu, icerik):
    try:
        if not os.environ.get("MAIL_USERNAME") or not os.environ.get("MAIL_PASSWORD"):
            print("MAIL_USERNAME veya MAIL_PASSWORD eksik.")
            return False

        mesaj = Message(
            subject=konu,
            recipients=[alici],
            body=icerik
        )

        mail.send(mesaj)
        return True

    except smtplib.SMTPAuthenticationError as e:
        print("SMTP kimlik doğrulama hatası:", e)
        return False

    except Exception as e:
        print("Mail gönderme hatası:", e)
        return False