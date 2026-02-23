from flask import Flask, render_template_string, request, jsonify
import requests
from openai import OpenAI

app = Flask(__name__)

# --- YAPILANDIRMA ---
SA_BEYIN_URL = "http://127.0.0.1:8080/v1/chat/completions"
SOL_BEYIN_KEYS = [
    {"id": 1, "key": "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", "status": "Hazır"},
    {"id": 2, "key": "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", "status": "Hazır"},
    {"id": 3, "key": "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", "status": "Hazır"}
]

# --- GÖRSEL ARAYÜZ (HTML/JS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Şenol AI Komuta Merkezi</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #0f172a; color: white; font-family: sans-serif; padding: 20px; }
        .dashboard { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
        .worker { padding: 10px; border-radius: 8px; border: 1px solid #334155; flex: 1; text-align: center; font-size: 12px; }
        .active { background: #1e293b; border-color: #38bdf8; }
        .exhausted { background: #450a0a; border-color: #ef4444; color: #f87171; }
        .ready { background: #064e3b; border-color: #10b981; }
        #chat { height: 300px; overflow-y: auto; background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #334155; }
        input { width: 100%; padding: 15px; border-radius: 8px; border: none; background: #334155; color: white; box-sizing: border-box; }
        .btn-group { margin-top: 10px; display: flex; gap: 5px; }
        button { flex: 1; padding: 10px; border-radius: 5px; border: none; cursor: pointer; font-weight: bold; }
        .btn-sol { background: #3b82f6; color: white; }
        .btn-sag { background: #f59e0b; color: white; }
    </style>
</head>
<body>
    <h2>Komuta Merkezi</h2>
    
    <div class="dashboard" id="worker-list">
        <div class="worker ready" id="sag-beyin">SAĞ BEYİN (Lokal)</div>
        {% for worker in workers %}
        <div class="worker ready" id="key-{{ worker.id }}">ANAHTAR {{ worker.id }}</div>
        {% endfor %}
    </div>

    <div id="chat"><i>Sistem hazır, görev bekleniyor...</i></div>
    
    <input type="text" id="userInput" placeholder="Görevi buraya yaz...">
    
    <div class="btn-group">
        <button class="btn-sol" onclick="ask('SOL')">SOL BEYİN (Bulut)</button>
        <button class="btn-sag" onclick="ask('SAG')">SAĞ BEYİN (Lokal)</button>
    </div>

    <script>
        async function ask(mode) {
            const input = document.getElementById('userInput');
            const chat = document.getElementById('chat');
            if(!input.value) return;

            chat.innerHTML += `<p><b>Sen:</b> ${input.value}</p>`;
            const prompt = input.value;
            input.value = "Yazıyor...";

            const response = await fetch('/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: prompt, mode: mode})
            });
            const data = await response.json();
            
            chat.innerHTML += `<p><b>AI:</b> ${data.answer}</p>`;
            chat.scrollTop = chat.scrollHeight;
            input.value = "";
            
            // Buton durumlarını güncelle
            updateStatus(data.worker_status);
        }

        function updateStatus(status) {
            status.forEach(w => {
                const el = document.getElementById('key-' + w.id);
                if(w.status === 'Doldu') el.className = 'worker exhausted';
                else el.className = 'worker ready';
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, workers=SOL_BEYIN_KEYS)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    prompt = data['prompt']
    mode = data['mode']
    answer = "Hata oluştu."

    if mode == "SAG":
        try:
            r = requests.post(SA_BEYIN_URL, json={"messages": [{"role": "user", "content": prompt}]})
            answer = r.json()['choices'][0]['message']['content']
        except: answer = "Sağ Beyin çevrimdışı! (Server'ı açmayı unutma)"
    
    else: # SOL BEYİN
        for worker in SOL_BEYIN_KEYS:
            if worker['status'] == "Hazır":
                try:
                    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=worker['key'])
                    r = client.chat.completions.create(
                        model="cognitivecomputations/dolphin-mixtral-8x7b",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    answer = r.choices[0].message.content
                    break
                except Exception as e:
                    if "429" in str(e) or "402" in str(e):
                        worker['status'] = "Doldu"
                    continue
        else: answer = "Tüm anahtarların kotası doldu! Yarın 03:00'te sıfırlanacak."

    return jsonify({"answer": answer, "worker_status": SOL_BEYIN_KEYS})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

