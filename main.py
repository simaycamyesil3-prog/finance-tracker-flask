from database import tablolari_olustur
from gelir import gelir_ekle, gelirleri_listele, gelir_sil, gelir_guncelle
from gider import gider_ekle, giderleri_listele, gider_sil, gider_guncelle
from rapor import finans_ozeti, istatistikler, kategori_analizi, arama_yap, csv_disari_aktar, son_10_islem, aylik_rapor
from auth import kayit_ol, giris_yap
from butce import butce_belirle,butce_uyarisi
from grafik import gelir_gider_grafigi


def menu_goster():
    print("\n===== FINANS TAKIP SISTEMI =====")
    print("1- Gelir Ekle")
    print("2- Gider Ekle")
    print("3- Finans Ozeti")
    print("4- Gelirleri Listele")
    print("5- Giderleri Listele")
    print("6- Gelir Sil")
    print("7- Gider Sil")
    print("8- Gelir Guncelle")
    print("9- Gider Guncelle")
    print("10- Istatistikler")
    print("11- Kategori Bazli Gider Analizi")
    print("12- Arama Yap")
    print("13- CSV Disari Aktar")
    print("14- Son 10 Islem")
    print("15- Aylik Rapor")
    print("16- Cikis")
    print("17- Kayit Ol")
    print("18- Giris Yap")
    print("19- butce belirle")
    print("20- Butce Durumu")
    print("21- Gelir / Gider Grafiği")


def main():
    tablolari_olustur()
    aktif_kullanici_id = None

    while True:
        menu_goster()
        secim = input("Seciminiz: ")

        if secim == "1":
            if aktif_kullanici_id:
                gelir_ekle(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")

        elif secim == "2":
            if aktif_kullanici_id:
                gider_ekle(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")

        elif secim == "3":
            if aktif_kullanici_id:
                finans_ozeti(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")

        elif secim == "4":
            if aktif_kullanici_id:
                gelirleri_listele(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")

        elif secim == "5":
            if aktif_kullanici_id:
                giderleri_listele(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")

        elif secim == "6":
            gelir_sil()

        elif secim == "7":
            gider_sil()

        elif secim == "8":
            gelir_guncelle()

        elif secim == "9":
            gider_guncelle()

        elif secim == "10":
            if aktif_kullanici_id:
                istatistikler(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")

        elif secim == "11":
            if aktif_kullanici_id:
                kategori_analizi(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")

        elif secim == "12":
            if aktif_kullanici_id:
                arama_yap(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")

        elif secim == "13":
            if aktif_kullanici_id:
                csv_disari_aktar(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")

        elif secim == "14":
            if aktif_kullanici_id:
                son_10_islem(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")

        elif secim == "15":
            if aktif_kullanici_id:
                aylik_rapor(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")

        elif secim == "16":
            print("Programdan çıkılıyor...")
            break

        elif secim == "17":
            kayit_ol()

        elif secim == "18":
            aktif_kullanici_id = giris_yap()

        elif secim == "19":
            if aktif_kullanici_id:
                butce_belirle(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")
        
        elif secim == "20":
            if aktif_kullanici_id:
                butce_uyarisi(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")
        
        elif secim == "21":
            if aktif_kullanici_id:
                gelir_gider_grafigi(aktif_kullanici_id)
            else:
                print("\n❌ Önce giriş yapmalısınız.")
        else:
            print("Hatalı seçim. Lütfen 1 ile 21 arasında bir değer giriniz.")


if __name__ == "__main__":
    main()