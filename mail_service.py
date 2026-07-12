import os
import random

import requests


def mail_ayarlari(app):
    # app.py içindeki mevcut mail_ayarlari(app) çağrısıyla
    # uyumlu kalması için bu fonksiyon bırakılıyor.
    pass


def kod_uret():
    return str(random.randint(100000, 999999))


def mail_gonder(alici, konu, icerik):
    script_url = os.environ.get("GOOGLE_SCRIPT_URL")
    secret_key = os.environ.get("GOOGLE_SCRIPT_SECRET")

    if not script_url or not secret_key:
        print("GOOGLE_SCRIPT_URL veya GOOGLE_SCRIPT_SECRET eksik.")
        return False

    veri = {
        "secret": secret_key,
        "alici": alici,
        "konu": konu,
        "icerik": icerik
    }

    try:
        cevap = requests.post(
            script_url,
            json=veri,
            timeout=15
        )

        if cevap.status_code != 200:
            print(
                "Google Apps Script HTTP hatası:",
                cevap.status_code,
                cevap.text
            )
            return False

        try:
            sonuc = cevap.json()
        except ValueError:
            print("Google Apps Script geçersiz yanıt verdi:", cevap.text)
            return False

        if sonuc.get("basarili") is True:
            print(f"E-posta başarıyla gönderildi: {alici}")
            return True

        print("Google Apps Script mail hatası:", sonuc.get("mesaj"))
        return False

    except requests.Timeout:
        print("Google Apps Script bağlantısı zaman aşımına uğradı.")
        return False

    except requests.RequestException as hata:
        print("Google Apps Script bağlantı hatası:", hata)
        return False

    except Exception as hata:
        print("Beklenmeyen mail gönderme hatası:", hata)
        return False