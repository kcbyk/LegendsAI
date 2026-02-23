# Sadece Architect (Mimar) kısmındaki kritik düzeltme:
@app.route('/api/architect', methods=['POST'])
def architect():
    data = request.json
    command = data.get('command')
    try:
        with open('dashboard.py', 'r') as f: current_code = f.read()
        prompt = f"Aşağıdaki Flask koduna şu özelliği ekle/güncelle. SADECE tam kodu döndür. HİÇBİR ÖZELLİĞİ SİLME.\\nKomut: {command}\\n\\nKod:\\n{current_code}"
        
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=API_KEYS[0])
        res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.1)
        new_code = res.choices[0].message.content
        
        # Markdown temizliği (Hata koruması)
        if "```python" in new_code: new_code = new_code.split("```python")[1].split("```")[0].strip()
        elif "```" in new_code: new_code = new_code.split("```")[1].split("```")[0].strip()

        with open('dashboard.py', 'w') as f: f.write(new_code)
        
        # ARKA PLANDA OTOMATİK YAYINLA
        os.system("git add dashboard.py")
        os.system(f"git commit -m 'Architect: {command}'")
        os.system("git push origin main") 

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

