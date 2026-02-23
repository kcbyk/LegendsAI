import sys
import requests
from openai import OpenAI

# 1. BULUT API ANAHTARLARI
API_ANAHTARLARI = [
    "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",
    "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",
    "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"
]

class HibritKomuta:
    def __init__(self):
        self.mod = "BULUT" # Varsayılan mod
        self.key_index = 0
        self.hafiza = [{"role": "system", "content": "Sen Şenol'un profesyonel hibrit mimarısın."}]
        self.baglan_bulut()
        self.lokal_url = "http://127.0.0.1:8080/v1/chat/completions"

    def baglan_bulut(self):
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_ANAHTARLARI[self.key_index])

    def mod_degistir(self):
        if self.mod == "BULUT":
            self.mod = "LOKAL"
            print("\n\033[93m[!] Mod Değişti: SAĞ BEYİN (Telefonun İçindeki Zeka) Aktif.\033[0m")
        else:
            self.mod = "BULUT"
            print("\n\033[92m[!] Mod Değişti: SOL BEYİN (Bulut / Devasa Ağ) Aktif.\033[0m")

    def sor(self, soru):
        if soru.lower() == 'switch':
            self.mod_degistir()
            return

        self.hafiza.append({"role": "user", "content": soru})
        print(f"\n\033[90m[ {self.mod} Üzerinden Yanıt Bekleniyor... ]\033[0m\n")

        if self.mod == "BULUT":
            try:
                response = self.client.chat.completions.create(
                    model="cognitivecomputations/dolphin-mixtral-8x7b",
                    messages=self.hafiza,
                    stream=True
                )
                self.akistir(response)
            except Exception as e:
                if "429" in str(e) or "limit" in str(e).lower():
                    print("\n[!] Bulut limiti doldu, yedek anahtara geçiliyor...")
                    if self.key_index < len(API_ANAHTARLARI) - 1:
                        self.key_index += 1
                        self.baglan_bulut()
                        self.sor(soru)
                    else:
                        print("[!] Tüm bulut anahtarları bitti! Otomatik LOKAL moda geçiliyor.")
                        self.mod = "LOKAL"
                        self.sor(soru)
        else:
            # LOKAL (Telefonun kendi işlemcisi)
            try:
                response = requests.post(self.lokal_url, json={"messages": self.hafiza, "stream": True}, stream=True)
                # Lokal yanıtı işle... (Basitleştirilmiş akış)
                print("[Lokal Zeka]: ", end="")
                # (Lokal akış kodu buraya gelecek)
            except:
                print("\n\033[91m[Hata] Sağ Beyin (Lokal Server) açık mı? Kontrol et!\033[0m")

    def akistir(self, response):
        tam_cevap = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                kelime = chunk.choices[0].delta.content
                sys.stdout.write(kelime)
                sys.stdout.flush()
                tam_cevap += kelime
        self.hafiza.append({"role": "assistant", "content": tam_cevap})
        print("\n")

# --- Başlatma ---
hibrit = HibritKomuta()
print("\033[94m=== HİBRİT KOMUTA MERKEZİ AKTİF ===\033[0m")
print("[-] 'switch' yazarak beyinler arası geçiş yapabilirsin.")
while True:
    komut = input("\033[95mŞenol (Görev) > \033[0m")
    if komut.lower() == 'q': break
    hibrit.sor(komut)

