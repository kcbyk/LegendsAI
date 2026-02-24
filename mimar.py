import os
import subprocess
from openai import OpenAI

# Senin ana API anahtarın
API_KEY = "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"
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=API_KEY)

def mimar_bot():
    print("🚀 LEGENDS AI MIMAR TERMINAL BASLADI")
    print("------------------------------------")
    
    # Kullanıcıdan tasarımı sor
    tasarim = input("🛠️  Uygulamada neyi degistireyim patron?: ")
    if not tasarim: return

    # Mevcut kodu oku
    with open('dashboard.py', 'r') as f: eski_kod = f.read()

    print("🧠 Mimar dusunuyor ve kodu baştan yazıyor...")
    
    prompt = f"Aşağıdaki Python Flask kodunu şu isteğe göre güncelle. HİÇBİR ŞEYİ SİLME. Sadece tam kodu döndür.\\nİstek: {tasarim}\\nKod:\\n{eski_kod}"
    
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    yeni_kod = res.choices[0].message.content

    # Temizlik yapalım
    if "```python" in yeni_kod: yeni_kod = yeni_kod.split("```python")[1].split("```")[0].strip()
    elif "```" in yeni_kod: yeni_kod = yeni_kod.split("```")[1].split("```")[0].strip()

    # Dosyayı güncelle
    with open('dashboard.py', 'w') as f: f.write(yeni_kod)
    print("✅ dashboard.py guncellendi!")

    # GitHub'a fırlat
    print("📦 GitHub'a gonderiliyor...")
    subprocess.run(["git", "add", "dashboard.py"])
    subprocess.run(["git", "commit", "-m", f"Architect: {tasarim}"])
    subprocess.run(["git", "push", "origin", "main"])
    print("🚀 ISLEM TAMAM! Site 2 dakikaya yenilenir.")

if __name__ == "__main__":
    mimar_bot()

