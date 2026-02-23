from flask import Flask, render_template_string, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# --- API ANAHTARLARI (TYPO DÜZELTİLDİ) ---
API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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"
]
current_key_index = 0
MODEL = "llama-3.3-70b-versatile"

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    global current_key_index
    data = request.json
    messages = data.get('messages', [])
    temp = data.get('settings', {}).get('temperature', 0.2)
    attempts = 0
    while attempts < len(API_KEYS):
        try:
            client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=API_KEYS[current_key_index])
            res = client.chat.completions.create(model=MODEL, messages=messages, temperature=temp)
            return jsonify({"answer": res.choices[0].message.content})
        except Exception as e:
            current_key_index = (current_key_index + 1) % len(API_KEYS)
            attempts += 1
    return jsonify({"answer": "❌ Sunucu hatası! Lütfen 1 dakika sonra tekrar dene patron."})

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
    <meta charset="UTF-8">
    <title>Legends Pro v22.1</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; height: 100dvh; display: flex; flex-direction: column; overflow: hidden; }
        .msg-user { background: #1A1A1A; border: 1px solid #333; border-radius: 12px; padding: 12px; margin: 8px 0 8px auto; max-width: 85%; }
        .msg-ai { padding: 12px 0; border-bottom: 1px solid #222; display: flex; gap: 12px; }
        pre { background: #0A0A0A !important; border: 1px solid #333; border-radius: 8px; padding: 40px 12px 12px 12px; margin: 12px 0; position: relative; overflow-x: auto; color: #fff; }
        .code-actions { position: absolute; top: 8px; right: 8px; display: flex; gap: 6px; }
        .code-btn { padding: 4px 8px; border-radius: 4px; font-size: 10px; background: #222; border: 1px solid #444; color: #aaa; cursor: pointer; }
        .sidebar { width: 260px; background: #000; border-right: 1px solid #222; display: none; }
        @media (min-width: 768px) { .sidebar { display: flex; flex-direction: column; } }
    </style>
</head>
<body>
    <div class="flex flex-1 overflow-hidden">
        <aside class="sidebar p-4"><h1 class="font-bold border-b border-[#222] pb-4 mb-4">LEGENDS PRO</h1><div id="history" class="flex-1 overflow-y-auto text-sm text-gray-500">Geçmiş yükleniyor...</div></aside>
        <main class="flex-1 flex flex-col relative">
            <header class="p-4 border-b border-[#222] flex justify-between md:hidden"><span class="font-bold">LEGENDS PRO</span></header>
            <div id="chat-container" class="flex-1 overflow-y-auto p-4 md:p-8 space-y-4">
                <div class="text-gray-600 text-center mt-20"><i class="fas fa-cube text-4xl mb-4"></i><br>Emirlerini bekliyorum Şenol.</div>
            </div>
            <div class="p-4 md:p-8 bg-gradient-to-t from-black to-transparent">
                <div class="max-w-3xl mx-auto bg-[#111] border border-[#333] rounded-xl p-2 flex items-end gap-2">
                    <textarea id="userInput" class="flex-1 bg-transparent border-none text-white p-2 text-sm focus:outline-none" placeholder="Buraya yaz..." rows="1"></textarea>
                    <button id="sendBtn" class="p-3 bg-white text-black rounded-lg hover:bg-gray-200 transition"><i class="fas fa-paper-plane"></i></button>
                </div>
            </div>
        </main>
    </div>

    <script>
        let history = [];
        const container = document.getElementById('chat-container');
        
        // MARKDOWN AYARLARI
        const renderer = new marked.Renderer();
        renderer.code = function(code, lang) {
            return `<div class="relative">
                <div class="code-actions">
                    <button onclick="copyCode(this)" class="code-btn">Kopyala</button>
                    <button onclick="updateCode(this)" class="code-btn">Güncelle v2</button>
                </div>
                <pre><code>${code}</code></pre>
            </div>`;
        };
        marked.setOptions({ renderer: renderer });

        window.copyCode = (btn) => { const code = btn.closest('.relative').querySelector('code').innerText; navigator.clipboard.writeText(code); btn.innerText = 'Alındı'; setTimeout(()=>btn.innerText='Kopyala', 2000); };
        window.updateCode = (btn) => { const code = btn.closest('.relative').querySelector('code').innerText; document.getElementById('userInput').value = `v2 sürümünü yap:\\n\\n\`\`\`\\n${code}\`\`\``; document.getElementById('userInput').focus(); };

        async function sendMessage() {
            const val = document.getElementById('userInput').value.trim();
            if(!val) return;
            
            if(history.length === 0) container.innerHTML = '';
            container.innerHTML += `<div class="msg-user">${val}</div>`;
            document.getElementById('userInput').value = "";
            
            const loadId = "ai_" + Date.now();
            container.innerHTML += `<div id="${loadId}" class="msg-ai text-gray-500 text-sm italic">Cevap yazılıyor...</div>`;
            container.scrollTop = container.scrollHeight;
            
            history.push({role: "user", content: val});

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ messages: history, settings: {temperature: 0.2} })
                });
                const data = await res.json();
                document.getElementById(loadId).remove();
                
                const aiDiv = document.createElement('div');
                aiDiv.className = 'msg-ai text-sm';
                aiDiv.innerHTML = `<div class="w-8 h-8 rounded-full border border-[#333] flex items-center justify-center bg-white text-black text-xs font-bold">ŞK</div><div class="flex-1 overflow-hidden">${marked.parse(data.answer)}</div>`;
                container.appendChild(aiDiv);
                history.push({role: "assistant", content: data.answer});
                container.scrollTop = container.scrollHeight;
            } catch(e) {
                document.getElementById(loadId).innerHTML = "❌ Hata: İnternet bağlantını kontrol et patron.";
            }
        }

        document.getElementById('sendBtn').onclick = sendMessage;
        document.getElementById('userInput').onkeydown = (e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } };
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

