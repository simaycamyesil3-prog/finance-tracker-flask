from datetime import datetime


GELIR_KATEGORILERI = ["Maas", "Burs", "Freelance", "Yatirim", "Diger"]

GIDER_KATEGORILERI = [
    "Market",
    "Kira",
    "Fatura",
    "Ulasim",
    "Yemek",
    "Eglence",
    "Saglik",
    "Egitim",
    "Diger"
]


def sayi_al(mesaj: str):
    while True:
        try:
            deger = float(input(mesaj))

            if deger <= 0:
                print("Tutar 0'dan buyuk olmali.")
            else:
                return deger

        except ValueError:
            print("Lutfen gecerli bir sayi giriniz.")


def tarih_al():
    tarih = input("Tarih giriniz (GG.AA.YYYY) / Bugun icin bos birakin: ")

    if tarih == "":
        return datetime.now().strftime("%d.%m.%Y")

    try:
        datetime.strptime(tarih, "%d.%m.%Y")
        return tarih
    except ValueError:
        print("Hatali tarih formati. Bugunun tarihi eklendi.")
        return datetime.now().strftime("%d.%m.%Y")


def kategori_sec(kategoriler: list[str]):
    print("\nKategoriler:")

    for i, kategori in enumerate(kategoriler, start=1):
        print(f"{i}- {kategori}")

    while True:
        try:
            secim = int(input("Kategori seciniz: "))

            if 1 <= secim <= len(kategoriler):
                return kategoriler[secim - 1]
            else:
                print("Gecersiz kategori secimi.")

        except ValueError:
            print("Lutfen sayi giriniz.")