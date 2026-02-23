#!/bin/bash

echo -e "\033[92m[+] Operasyon Başlıyor: Şenol AI İmparatorluğu uyanıyor...\033[0m"

# 1. SAĞ BEYİN (Lokal) - Arka planda sessizce başlatılıyor
# '&' işareti bu işin arka planda akmasını sağlar.
./build/bin/llama-server -m models/qwen2.5-coder-3b.gguf -c 2048 -t 4 --port 8080 > /dev/null 2>&1 &

echo -e "\033[94m[i] Sağ Beyin (Lokal) motoru rölantide çalışıyor...\033[0m"

# Lokal server'ın ısınması için 5 saniye bekle
sleep 5

# 2. SOL BEYİN (Dashboard) - Ön planda başlatılıyor
echo -e "\033[92m[+] Sol Beyin (Görsel Panel) ateşleniyor!\033[0m"
python dashboard.py

