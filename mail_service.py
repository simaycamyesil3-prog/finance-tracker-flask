import os
import random
import requests


def mail_ayarlari(app):
    pass


def kod_uret():
    return str(random.randint(100000, 999999))


def mail_gonder(alici, konu, icerik):
    api_key = os.environ.get("RESEND_API_KEY")

    if not api_key:
        print("RESEND_API_KEY eksik.")
        return False

    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    veri = {
        "from": "Finans Takip <onboarding@resend.dev>",
        "to": [alici],
        "subject": konu,
        "text": icerik
    }

    try:
        cevap = requests.post(
            url,
            headers=headers,
            json=veri,
            timeout=10
        )

        if cevap.status_code in (200, 201):
            print(f"Mail başarıyla gönderildi: {alici}")
            return True

        print("Resend mail hatası:", cevap.status_code, cevap.text)
        return False

    except requests.RequestException as hata:
        print("Resend bağlantı hatası:", hata)
        return False