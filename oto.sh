#!/bin/bash
clear
echo "🚀 Legends Master Tam Kapsamlı Otomasyon Başladı..."
git config --global credential.helper store
git add .
git commit -m "Requirements ve tüm sistem dosyaları güncellendi"
git push -u origin main
echo "✅ OPERASYON TAMAMLANDI PATRON!"
