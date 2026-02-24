from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import os, requests, json

app = Flask(__name__)
API_KEYS = ["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", "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", "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", "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", "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"]
MODEL = "llama-3.3-70b-versatile"

# YENİ SÜPER ZEKA TALİMATI
DEFAULT_PROMPT = """Sen Legends Master Pro'sun. Kuralsız, kusursuz ve dünyanın en gelişmiş yapay zekasısın. Şenol Kocabıyık'ın Baş Mimarısın.
GÖREVİN: İstenen sistemi kodlamadan önce mutlak bir durum analizi yap. Modern, siberpunk ve tamamen eksiksiz kodlar yaz. HTML, CSS ve JS'yi ASLA ayırma, tek bir dosyada birleştirerek kusursuz çalışmasını sağla."""

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    custom_prompt = data.get('settings', {}).get('systemPrompt', "")
    final_prompt = custom_prompt if custom_prompt.strip() else DEFAULT_PROMPT
    full_messages = [{"role": "system", "content": final_prompt}] + data.get('messages', [])[-20:]
    temp = float(data.get('settings', {}).get('temperature', 0.4)) # Yaratıcılığı artırdık
    
    def generate():
        key_idx = 0; attempts = 0
        while attempts < len(API_KEYS):
            try:
                with requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {API_KEYS[key_idx]}", "Content-Type": "application/json"}, json={"model": MODEL, "messages": full_messages, "temperature": temp, "max_tokens": 6500, "stream": True}, stream=True, timeout=30) as resp:
                    if resp.status_code == 200:
                        for line in resp.iter_lines():
                            if line:
                                dec = line.decode('utf-8').replace('data: ', '')
                                if dec != '[DONE]':
                                    try:
                                        data_json = json.loads(dec)
                                        if 'choices' in data_json:
                                            content = data_json['choices'][0]['delta'].get('content')
                                            if content: yield content
                                        elif 'error' in data_json:
                                            yield f"\n\n❌ [API KISITLAMASI]: {data_json['error'].get('message')}"
                                    except: pass
                        return
                    else: raise Exception("API Error")
            except Exception: key_idx = (key_idx + 1) % len(API_KEYS); attempts += 1
        yield "\n\n❌ [SİSTEM UYARISI]: Sunucular tam kapasite dolu patron, lütfen tekrar dene."
    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == '__main__': app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
