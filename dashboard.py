#!/bin/bash
clear
echo "🚀 Legends AI Otomasyon Botu Başladı..."
echo "🧹 Eski kod temizleniyor..."
rm -f dashboard.py

echo "📝 Nano açılıyor... Yeni kodu yapıştır, CTRL+O, Enter, CTRL+X yap!"
sleep 2
nano dashboard.py

# Şifre sormaması için ayarı zorla açıyoruz
git config --global credential.helper store

echo "⚙️ Kodlar paketleniyor..."
git add dashboard.py

echo "📦 GitHub'a fırlatılıyor..."
git commit -m "Legends AI Master Update"
git push -u origin main

echo "✅ OPERASYON TAMAMLANDI PATRON!"
echo "🌐 Render'ın yeşil ışığının yanması için 2-3 dakika bekle."

