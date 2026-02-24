import os

print("🤖 Legends Asistan Botu Çalışıyor...")

if not os.path.exists('update.txt'):
    print("❌ 'update.txt' dosyası yok! Lütfen kodları bu dosyaya yapıştırıp tekrar dene.")
    exit()

with open('update.txt', 'r', encoding='utf-8') as f:
    icerik = f.read()

bolumler = icerik.split('===FILE: ')

if len(bolumler) <= 1:
    print("❌ Format hatası! AI'dan gelen kodda '===FILE:' etiketi bulunamadı.")
    exit()

for bolum in bolumler[1:]:
    satirlar = bolum.split('\n')
    dosya_yolu = satirlar[0].strip().replace('===', '')
    
    kod_blogu = bolum.split('===END===')[0]
    kod = '\n'.join(kod_blogu.split('\n')[1:]).strip()
    
    if kod.startswith('```'):
        kod = '\n'.join(kod.split('\n')[1:])
    if kod.endswith('```'):
        kod = '\n'.join(kod.split('\n')[:-1])

    klasor = os.path.dirname(dosya_yolu)
    if klasor and not os.path.exists(klasor):
        os.makedirs(klasor)

    with open(dosya_yolu, 'w', encoding='utf-8') as f:
        f.write(kod.strip() + '\n')
    
    print(f"✅ Dosya Yenilendi: {dosya_yolu}")

print("🚀 Tüm mimari başarıyla inşa edildi!")
print("🌍 GitHub'a fırlatılıyor...")
os.system('chmod +x oto.sh && ./oto.sh')
