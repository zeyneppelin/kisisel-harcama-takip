import csv
import os
from datetime import datetime

CSV_DOSYA_ADI = "kayitlar1.csv"
PARA_BIRIMI = "TL"

KATEGORILER = [
    "maaş",
    "market",
    "yemek",
    "kira",
    "ulaşım",
    "eğlence",
    "sağlık",
    "fatura",
    "diğer"
]


def csv_var_mi():
    """CSV dosyası var mı kontrol eder, yoksa başlık satırı ile oluşturur."""
    if not os.path.exists(CSV_DOSYA_ADI):
        with open(CSV_DOSYA_ADI, mode="w", newline="", encoding="utf-8") as f:
            yazici = csv.writer(f)
            yazici.writerow(["tarih", "tip", "kategori", "aciklama", "tutar"])


def kategori_sec():
    """Kullanıcıya kategorileri listeleyip seçim yaptırır."""
    print("\nKategori seçiniz:")
    for i, kat in enumerate(KATEGORILER, start=1):
        print(f"{i}) {kat}")
    while True:
        secim = input("Kategori numarası: ").strip()
        if secim.isdigit():
            idx = int(secim)
            if 1 <= idx <= len(KATEGORILER):
                return KATEGORILER[idx - 1]
        print("Geçersiz seçim, lütfen listedeki numaralardan birini girin.")


def tarih_al():
    """
    Kullanıcıdan tarih alır.
    Boş bırakılırsa bugünün tarihi döner.
    Format: YYYY-MM-DD
    """
    giris = input("Tarih (YYYY-AA-GG, boş bırakılırsa bugün): ").strip()
    if giris == "":
        return datetime.today().strftime("%Y-%m-%d")

    while True:
        try:
            dt = datetime.strptime(giris, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            print("Tarih formatı hatalı. Örnek: 2025-03-01")
            giris = input("Tarih (YYYY-AA-GG): ").strip()


def kayit_ekle(tip):
    """Yeni gelir veya gider ekler."""
    print(f"\n--- Yeni {tip.upper()} kaydı ---")
    tarih = tarih_al()
    kategori = kategori_sec()
    aciklama = input("Açıklama (boş bırakılabilir): ").strip()

    while True:
        tutar_girdi = input(f"Tutar ({PARA_BIRIMI}, örn: 150.75): ").replace(",", ".").strip()
        try:
            tutar = float(tutar_girdi)
            if tutar <= 0:
                print("Tutar pozitif olmalıdır.")
                continue
            break
        except ValueError:
            print("Lütfen geçerli bir sayı girin.")

    with open(CSV_DOSYA_ADI, mode="a", newline="", encoding="utf-8") as f:
        yazici = csv.writer(f)
        yazici.writerow([tarih, tip, kategori, aciklama, tutar])

    print(f"\n✅ {tip.upper()} kaydı eklendi!\n")


def kayitlari_oku():
    """CSV dosyasından tüm kayıtları okur ve liste olarak döner."""
    kayitlar = []
    if not os.path.exists(CSV_DOSYA_ADI):
        return kayitlar

    with open(CSV_DOSYA_ADI, mode="r", newline="", encoding="utf-8") as f:
        okuyucu = csv.DictReader(f)
        for satir in okuyucu:
            satir["tutar"] = float(satir["tutar"])
            kayitlar.append(satir)
    return kayitlar


def kayitlari_listele():
    """Tüm gelir/gider kayıtlarını ekrana yazdırır."""
    kayitlar = kayitlari_oku()
    if not kayitlar:
        print("\nHenüz hiç kayıt yok.\n")
        return

    print("\n----- TÜM KAYITLAR -----")
    for satir in kayitlar:
        print(
            f"{satir['tarih']} | {satir['tip']:5} | "
            f"{satir['kategori']:10} | {satir['aciklama'][:20]:20} | {satir['tutar']:.2f} {PARA_BIRIMI}"
        )
    print("-------------------------\n")


def genel_rapor():
    """Tüm kayıtlar üzerinden genel rapor oluşturur."""
    kayitlar = kayitlari_oku()
    if not kayitlar:
        print("\nHenüz hiç kayıt yok, rapor oluşturulamıyor.\n")
        return

    rapor_hesapla_ve_yazdir(kayitlar, baslik="GENEL RAPOR")


def aylik_rapor():
    """Belirli bir ay için rapor oluşturur (YYYY-MM)."""
    kayitlar = kayitlari_oku()
    if not kayitlar:
        print("\nHenüz hiç kayıt yok, rapor oluşturulamıyor.\n")
        return

    ay_girdisi = input("Raporlanacak ay (YYYY-AA, örn: 2025-03): ").strip()
    try:
        datetime.strptime(ay_girdisi, "%Y-%m")
    except ValueError:
        print("Tarih formatı hatalı. Örnek giriş: 2025-03\n")
        return

    filtreli = [k for k in kayitlar if k["tarih"].startswith(ay_girdisi)]
    if not filtreli:
        print(f"\n{ay_girdisi} ayında kayıt bulunamadı.\n")
        return

    rapor_hesapla_ve_yazdir(filtreli, baslik=f"{ay_girdisi} AYLIK RAPORU")


def rapor_hesapla_ve_yazdir(kayitlar, baslik="RAPOR"):
    """Verilen kayıt listesi için rapor hesaplar ve ekrana yazar."""
    toplam_gelir = 0.0
    toplam_gider = 0.0
    kategori_giderleri = {}

    for satir in kayitlar:
        if satir["tip"] == "gelir":
            toplam_gelir += satir["tutar"]
        elif satir["tip"] == "gider":
            toplam_gider += satir["tutar"]
            kategori = satir["kategori"]
            kategori_giderleri[kategori] = kategori_giderleri.get(kategori, 0) + satir["tutar"]

    net_bakiye = toplam_gelir - toplam_gider

    en_cok_kategori = None
    en_cok_tutar = 0.0
    if kategori_giderleri:
        en_cok_kategori = max(kategori_giderleri, key=kategori_giderleri.get)
        en_cok_tutar = kategori_giderleri[en_cok_kategori]

    print(f"\n----- {baslik} -----")
    print(f"Toplam Gelir : {toplam_gelir:.2f} {PARA_BIRIMI}")
    print(f"Toplam Gider : {toplam_gider:.2f} {PARA_BIRIMI}")
    print(f"Net Bakiye   : {net_bakiye:.2f} {PARA_BIRIMI}")

    if en_cok_kategori:
        print(f"En çok harcama yapılan kategori: {en_cok_kategori} ({en_cok_tutar:.2f} {PARA_BIRIMI})")
    else:
        print("Kategori bazlı gider bulunamadı.")
    print("-------------------------\n")


def menuyu_goster():
    print("===== KİŞİSEL HARCAMA TAKİP UYGULAMASI =====")
    print("1) Gelir ekle")
    print("2) Gider ekle")
    print("3) Kayıtları listele")
    print("4) Genel rapor göster")
    print("5) Aylık rapor göster")
    print("6) Çıkış")
    print("============================================")


def main():
    csv_var_mi()

    while True:
        menuyu_goster()
        secim = input("Seçiminiz (1-6): ").strip()

        if secim == "1":
            kayit_ekle("gelir")
        elif secim == "2":
            kayit_ekle("gider")
        elif secim == "3":
            kayitlari_listele()
        elif secim == "4":
            genel_rapor()
        elif secim == "5":
            aylik_rapor()
        elif secim == "6":
            print("\nProgramdan çıkılıyor. Görüşmek üzere! 👋\n")
            break
        else:
            print("\nGeçersiz seçim, lütfen 1-6 arası bir değer girin.\n")


if __name__ == "__main__":
    main()
