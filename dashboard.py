#!/bin/bash
clear
echo "🚀 Legends AI Mimar Botu Başladı..."
rm -f dashboard.py
echo "📝 Yeni kodu yapıştır (CTRL+O, Enter, CTRL+X)"
nano dashboard.py

# Şifre sormaması için ayarı zorla açıyoruz
git config --global credential.helper store

echo "📦 GitHub'a fırlatılıyor..."
git add dashboard.py
git commit -m "Mimar Guncellemesi"
git push -u origin main

echo "✅ TAMAMDIR PATRON! 3 Dakika bekle Render yenilensin."

