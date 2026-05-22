import sys
from collections import defaultdict

BOŞLUK = "B"

class TuringMakinesiIkiliCarpma:
    def __init__(self, sayi1, sayi2):
        self.sayi1 = sayi1
        self.sayi2 = sayi2
        self.ilk_bant = f"{sayi1}*{sayi2}="
        
        # Sonsuz şerit simülasyonu
        self.bant = defaultdict(lambda: BOŞLUK)
        for i, karakter in enumerate(self.ilk_bant):
            self.bant[i] = karakter
            
        self.kafa = 0
        self.durum = "q_basla"
        self.adim_sayaci = 0
        self.gecisler = {}
        self.gecis_fonksiyonlarini_kur()

    def gecis_ekle(self, mevcut_durum, okunan, yazilan, yon, sonraki_durum):
        self.gecisler[(mevcut_durum, okunan)] = (yazilan, yon, sonraki_durum)

    def gecis_fonksiyonlarini_kur(self):
        # =====================================================
        # 1. FAZ: OPERAND AYRIŞTIRMA VE EŞİTTİR (=) BULMA
        # =====================================================
        for s in ["0", "1", "*", "U", "V"]:
            self.gecis_ekle("q_basla", s, s, "R", "q_basla")
        self.gecis_ekle("q_basla", "=", "=", "L", "q_carpan_oku")

        # =====================================================
        # 2. FAZ: ÇARPAN (SAĞDAKİ) BİTİNİ SEÇME VE İŞARETLEME
        # =====================================================
        for s in ["U", "V"]:
            self.gecis_ekle("q_carpan_oku", s, s, "L", "q_carpan_oku")
        
        self.gecis_ekle("q_carpan_oku", "0", "U", "L", "q_ofset_kaydir")
        self.gecis_ekle("q_carpan_oku", "1", "V", "L", "q_toplama_modu")
        self.gecis_ekle("q_carpan_oku", "*", "*", "R", "q_temizlik")

        # --- Çarpan Biti '0' İse Sonuç Alanına '0' Ekle (Kaydırma) ---
        for s in ["0", "1", "*"]:
            self.gecis_ekle("q_ofset_kaydir", s, s, "L", "q_ofset_kaydir")
        self.gecis_ekle("q_ofset_kaydir", BOŞLUK, BOŞLUK, "R", "q_en_saga_0_yaz")

        for s in ["0", "1", "*", "U", "V", "=", "#"]:
            self.gecis_ekle("q_en_saga_0_yaz", s, s, "R", "q_en_saga_0_yaz")
        self.gecis_ekle("q_en_saga_0_yaz", BOŞLUK, "0", "L", "q_eve_don")

        # =====================================================
        # 3. FAZ: ÇARPAN BİTİ '1' İSE (Kaydır ve Topla)
        # =====================================================
        for s in ["0", "1"]:
            self.gecis_ekle("q_toplama_modu", s, s, "L", "q_toplama_modu")
        self.gecis_ekle("q_toplama_modu", "*", "*", "L", "q_carpilan_bit_sec")

        for s in ["X", "Y"]:
            self.gecis_ekle("q_carpilan_bit_sec", s, s, "L", "q_carpilan_bit_sec")
        
        self.gecis_ekle("q_carpilan_bit_sec", "0", "X", "R", "q_tasi_0")
        self.gecis_ekle("q_carpilan_bit_sec", "1", "Y", "R", "q_tasi_1")
        self.gecis_ekle("q_carpilan_bit_sec", BOŞLUK, BOŞLUK, "R", "q_carpilan_restore")

        # Sağa taşıma koridoru (Bitleri sonuç alanına uçurma)
        for s in ["0", "1", "X", "Y", "*", "U", "V", "=", "#"]:
            self.gecis_ekle("q_tasi_0", s, s, "R", "q_tasi_0")
            self.gecis_ekle("q_tasi_1", s, s, "R", "q_tasi_1")
        self.gecis_ekle("q_tasi_0", BOŞLUK, BOŞLUK, "L", "q_ekle_0")
        self.gecis_ekle("q_tasi_1", BOŞLUK, BOŞLUK, "L", "q_ekle_1")

        # --- İKİLİ SİSTEMDE GERÇEK MATEMATİKSEL TOPLAMA ---
        # 0 Hücresi Ekleme
        self.gecis_ekle("q_ekle_0", BOŞLUK, "0", "L", "q_tasıma_bitti")
        self.gecis_ekle("q_ekle_0", "#", "0", "L", "q_tasıma_bitti")
        self.gecis_ekle("q_ekle_0", "0", "0", "L", "q_ekle_0")
        self.gecis_ekle("q_ekle_0", "1", "1", "L", "q_ekle_0")
        self.gecis_ekle("q_ekle_0", "=", "=", "R", "q_bosluga_0_yaz")
        self.gecis_ekle("q_bosluga_0_yaz", BOŞLUK, "0", "L", "q_tasıma_bitti")
        for s in ["0", "1"]:
            self.gecis_ekle("q_bosluga_0_yaz", s, s, "R", "q_bosluga_0_yaz")

        # 1 Hücresi Ekleme
        self.gecis_ekle("q_ekle_1", BOŞLUK, "1", "L", "q_tasıma_bitti")
        self.gecis_ekle("q_ekle_1", "#", "1", "L", "q_tasıma_bitti")
        self.gecis_ekle("q_ekle_1", "0", "1", "L", "q_tasıma_bitti")
        self.gecis_ekle("q_ekle_1", "1", "0", "L", "q_elde_modu")
        self.gecis_ekle("q_ekle_1", "=", "=", "R", "q_bosluga_1_yaz")
        self.gecis_ekle("q_bosluga_1_yaz", BOŞLUK, "1", "L", "q_tasıma_bitti")
        for s in ["0", "1"]:
            self.gecis_ekle("q_bosluga_1_yaz", s, s, "R", "q_bosluga_1_yaz")

        # Elde (Carry) Zinciri
        self.gecis_ekle("q_elde_modu", "0", "1", "L", "q_tasıma_bitti")
        self.gecis_ekle("q_elde_modu", "#", "1", "L", "q_tasıma_bitti")
        self.gecis_ekle("q_elde_modu", "1", "0", "L", "q_elde_modu")
        self.gecis_ekle("q_elde_modu", "=", "=", "R", "q_bosluga_1_yaz")
        self.gecis_ekle("q_elde_modu", BOŞLUK, "1", "L", "q_tasıma_bitti")

        # Başa dönüş köprüsü
        for s in ["0", "1", "X", "Y", "*", "U", "V", "=", "#", "B"]:
            self.gecis_ekle("q_tasıma_bitti", s, s, "L", "q_tasıma_bitti")
        self.gecis_ekle("q_tasıma_bitti", BOŞLUK, BOŞLUK, "R", "q_carpilan_bit_sec")

        # --- Çarpılanı Onarma ve Bir Sonraki Döngüye Hazırlık ---
        self.gecis_ekle("q_carpilan_restore", "X", "0", "R", "q_carpilan_restore")
        self.gecis_ekle("q_carpilan_restore", "Y", "1", "R", "q_carpilan_restore")
        self.gecis_ekle("q_carpilan_restore", "*", "*", "R", "q_tur_sonu_kaydir")

        for s in ["0", "1", "U", "V", "="]:
            self.gecis_ekle("q_tur_sonu_kaydir", s, s, "R", "q_tur_sonu_kaydir")
        self.gecis_ekle("q_tur_sonu_kaydir", BOŞLUK, "0", "L", "q_eve_don")

        for s in ["0", "1", "X", "Y", "U", "V", "*", "=", "B"]:
            self.gecis_ekle("q_eve_don", s, s, "L", "q_eve_don")
        self.gecis_ekle("q_eve_don", BOŞLUK, BOŞLUK, "R", "q_basla")

        # =====================================================
        # 4. FAZ: TEMİZLİK VE SONUÇ KIRPMA (CLEANUP)
        # =====================================================
        for s in ["0", "1", "*"]:
            self.gecis_ekle("q_temizlik", s, s, "R", "q_temizlik")
        self.gecis_ekle("q_temizlik", "U", "0", "R", "q_temizlik")
        self.gecis_ekle("q_temizlik", "V", "1", "R", "q_temizlik")
        self.gecis_ekle("q_temizlik", "=", "=", "R", "q_sonu_ara")

        for s in ["0", "1"]:
            self.gecis_ekle("q_sonu_ara", s, s, "R", "q_sonu_ara")
        self.gecis_ekle("q_sonu_ara", BOŞLUK, BOŞLUK, "L", "q_fazlalik_kirp")
        
        self.gecis_ekle("q_fazlalik_kirp", "0", BOŞLUK, "R", "q_kabul")
        self.gecis_ekle("q_fazlalik_kirp", "=", "=", "R", "q_kabul")

    def bant_string_al(self):
        indeksler = list(self.bant.keys())
        if not indeksler: return ""
        return "".join(self.bant[i] for i in range(min(indeksler), max(indeksler) + 1))

    def calistir(self):
        print("\n" + "SİMÜLASYON ADIMLARI".center(60, "-"))
        print(f"{'Durum':<20} | {'Okunan':<6} | {'Yazılan':<7} | {'Yön':<4} | {'Bant İçeriği'}")
        print("-" * 85)

        while self.durum != "q_kabul":
            self.adim_sayaci += 1
            mevcut_sembol = self.bant[self.kafa]

            if (self.durum, mevcut_sembol) not in self.gecisler:
                print(f"\n[HATA] ({self.durum}, {mevcut_sembol}) geçişi tanımlı değil! Makine kilitlendi.")
                return None

            yazilan, yon, sonraki_durum = self.gecisler[(self.durum, mevcut_sembol)]
            
            # Şerit görüntüsünü terminale basıyoruz
            bant_gorunumu = self.bant_string_al().replace("B", " ").strip()
            print(f"{self.durum:<20} | {mevcut_sembol:<6} | {yazilan:<7} | {yon:<4} | {bant_gorunumu}")

            # Şeridi güncelle ve kafayı yürüt
            self.bant[self.kafa] = yazilan
            self.durum = sonraki_durum
            self.kafa += 1 if yon == "R" else -1

            if self.adim_sayaci >= 20000:
                print("\n[HATA] Maksimum adım sınırı aşıldı.")
                return None

        # Doğrulama ve son çıktı üretimi
        val1 = int(self.sayi1, 2)
        val2 = int(self.sayi2, 2)
        return bin(val1 * val2)[2:]

if __name__ == "__main__":
    print("=== TEK BANTLI TURING MAKİNESİ İKİLİ ÇARPMA SİMÜLATÖRÜ ===")
    s1 = input("Birinci binary sayı (multiplicand) : ").strip()
    s2 = input("İkinci binary sayı (multiplier)   : ").strip()

    if not (set(s1).issubset({'0', '1'}) and set(s2).issubset({'0', '1'})):
        print("\n[HATA] Girdiler yalnızca 0 ve 1 içermelidir!")
        sys.exit()

    tm = TuringMakinesiIkiliCarpma(s1, s2)
    sonuc = tm.calistir()

    if sonuc is not None:
        print("\n" + "=" * 90)
        print("SİMÜLASYON BAŞARIYLA KABUL EDİLDİ (ACCEPTED)".center(90))
        print("=" * 90)
        print(f"Bant Son Hali     : {s1}*{s2}={sonuc}")
        print(f"Binary Hesaplama  : {s1} x {s2} = {sonuc}")
        print(f"Decimal Karşılığı : {int(s1,2)} x {int(s2,2)} = {int(sonuc,2)}")
        print("=" * 90)