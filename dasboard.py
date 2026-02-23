from flask import Flask, render_template_string, request, jsonify
import requests, json, os
from openai import OpenAI

app = Flask(__name__)

# --- LEGENDS AI V10 CORE (1 MİLYON TOKEN KAPASİTESİ) ---
# Patronun tüm anahtarları sisteme %100 uyumlu gömüldü
API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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"
]

current_key_index = 0
MODEL = "llama-3.3-70b-versatile"
chat_memory = []

SETTINGS = {
    "system_prompt": "Sen Legends AI'sın. Şenol'un baş yazılım mimarısın. 1) Sadece kod yaz. 2) Asla yarıda kesme. 3) Tek HTML dosyasında kusursuz iş çıkar. 4) Profesyonel ve ciddi bir ton kullan.",
    "temperature": 0.2,
    "theme_color": "#f97316"
}

def reset_memory():
    global chat_memory
    chat_memory = [{"role": "system", "content": SETTINGS["system_prompt"]}]

reset_memory()

# --- PWA GEREKLİLİKLERİ (APK İÇİN ŞART) ---
@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Legends AI Master",
        "short_name": "LegendsAI",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#020617",
        "theme_color": SETTINGS["theme_color"],
        "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/2103/2103633.png", "sizes": "512x512", "type": "image/png"}]
    })

@app.route('/sw.js')
def sw():
    return "self.addEventListener('fetch', function(event) {});", 200, {'Content-Type': 'application/javascript'}

# --- LEGENDS AI PREMİUM UI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>LEGENDS AI | PREMİUM</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
    <link rel="manifest" href="/manifest.json">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root { --primary: #f97316; --bg: #020617; --card: rgba(15, 23, 42, 0.85); }
        body { background: var(--bg); color: #f1f5f9; font-family: 'Inter', sans-serif; height: 100dvh; display: flex; flex-direction: column; overflow: hidden; margin: 0; }
        
        .glass { background: var(--card); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .neon-glow { box-shadow: 0 0 20px rgba(249, 115, 22, 0.2); }

        header { padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; z-index: 50; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .logo { font-weight: 900; font-size: 1.3rem; display: flex; align-items: center; gap: 8px; }
        .logo i { color: var(--primary); text-shadow: 0 0 10px var(--primary); }

        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; scroll-behavior: smooth; }
        .msg { max-width: 92%; padding: 16px 20px; border-radius: 24px; line-height: 1.6; font-size: 15px; animation: slideIn 0.3s ease; }
        .msg-user { align-self: flex-end; background: var(--primary); color: white; border-bottom-right-radius: 4px; }
        .msg-ai { align-self: flex-start; background: rgba(30, 41, 59, 0.7); border-bottom-left-radius: 4px; width: 100%; }
        
        #magic-menu { display: none; position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); width: 92%; max-width: 450px; z-index: 100; border-radius: 32px; padding: 12px; }
        .menu-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
        .menu-item { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 18px; border-radius: 20px; background: rgba(255,255,255,0.03); cursor: pointer; }
        .menu-item:active { transform: scale(0.9); background: rgba(255,255,255,0.1); }

        .input-area { padding: 16px; padding-bottom: max(16px, env(safe-area-inset-bottom)); }
        .input-box { border-radius: 28px; padding: 8px 8px 8px 18px; display: flex; align-items: flex-end; gap: 12px; }
        textarea { flex: 1; background: transparent; border: none; outline: none; color: white; max-height: 140px; resize: none; font-size: 16px; padding: 10px 0; }
        
        .circle-btn { width: 48px; height: 48px; border-radius: 50%; display: flex; justify-content: center; align-items: center; cursor: pointer; transition: 0.3s; }
        .btn-magic { background: rgba(255,255,255,0.05); }
        .btn-magic.active { transform: rotate(45deg); background: var(--primary); color: white; }
        .btn-send { background: var(--primary); color: white; }

        .action-row { display: flex; gap: 8px; margin-top: 15px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.05); }
        .act-btn { padding: 8px 14px; border-radius: 10px; font-size: 10px; font-weight: bold; background: rgba(255,255,255,0.04); }

        pre { background: #000 !important; border-radius: 16px; padding: 14px; margin: 10px 0; overflow-x: auto; border: 1px solid rgba(255,255,255,0.05); }
        code { font-family: 'Fira Code', monospace; font-size: 13px; }
        
        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>

    <header class="glass">
        <div class="logo"><i class="fas fa-crown"></i> LEGENDS AI</div>
        <button onclick="toggleModal('settingsModal')" class="text-gray-400 text-xl"><i class="fas fa-sliders-h"></i></button>
    </header>

    <div id="chat-container">
        <div class="msg msg-ai glass"><b>Legends AI:</b> Hazır mısın patron? V10 çekirdek sistemi ve 1 milyon token gücüyle emrindeyim.</div>
    </div>

    <div id="magic-menu" class="glass neon-glow">
        <div class="menu-grid">
            <div class="menu-item" onclick="setBrain('SOL')"><i class="fas fa-bolt text-orange-500"></i><span class="text-[9px] font-bold">CORE BEYİN</span></div>
            <div class="menu-item" onclick="setBrain('SAG')"><i class="fas fa-microchip text-blue-500"></i><span class="text-[9px] font-bold">LOCAL NODE</span></div>
            <div class="menu-item" onclick="triggerFile()"><i class="fas fa-folder-plus text-purple-500"></i><span class="text-[9px] font-bold">DOSYA EKLE</span></div>
            <div class="menu-item" onclick="alert('Görsel analiz v2 aktifleşiyor...')"><i class="fas fa-camera text-green-500"></i><span class="text-[9px] font-bold">FOTOĞRAF</span></div>
            <div class="menu-item" onclick="resetAI()"><i class="fas fa-trash text-red-500"></i><span class="text-[9px] font-bold">SIFIRLA</span></div>
            <div class="menu-item" onclick="toggleModal('settingsModal')"><i class="fas fa-cog text-gray-400"></i><span class="text-[9px] font-bold">AYARLAR</span></div>
        </div>
    </div>

    <div class="input-area">
        <div class="input-box glass">
            <div id="magicBtn" onclick="toggleMagic()" class="circle-btn btn-magic"><i class="fas fa-plus"></i></div>
            <textarea id="userInput" placeholder="Yazılım emrini ver..." rows="1" oninput="this.style.height='auto';this.style.height=this.scrollHeight+'px'"></textarea>
            <div onclick="sendMsg()" class="circle-btn btn-send"><i class="fas fa-paper-plane"></i></div>
        </div>
    </div>

    <input type="file" id="fileInput" class="hidden" onchange="handleFile(this)">

    <div id="settingsModal" class="fixed inset-0 bg-black/90 z-[110] hidden flex items-center justify-center p-6 backdrop-blur-sm">
        <div class="glass w-full max-w-sm rounded-[32px] p-8">
            <h2 class="text-xl font-black mb-6 flex items-center gap-3"><i class="fas fa-cog text-orange-500"></i> AYARLAR</h2>
            <div class="space-y-6">
                <div>
                    <label class="text-[10px] font-bold text-gray-500 uppercase mb-2 block">AI System Prompt</label>
                    <textarea id="set-prompt" class="w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-sm h-32 text-white outline-none"></textarea>
                </div>
                <div>
                    <label class="text-[10px] font-bold text-gray-500 uppercase mb-2 block">Tema Rengi</label>
                    <div class="flex gap-3">
                        <div onclick="setTheme('orange', '#f97316')" class="w-10 h-10 rounded-full bg-orange-500 border-2 border-white"></div>
                        <div onclick="setTheme('blue', '#3b82f6')" class="w-10 h-10 rounded-full bg-blue-500"></div>
                        <div onclick="setTheme('purple', '#a855f7')" class="w-10 h-10 rounded-full bg-purple-500"></div>
                    </div>
                </div>
            </div>
            <button onclick="saveSettings()" class="w-full bg-orange-600 py-4 rounded-2xl font-bold mt-8">GÜNCELLE</button>
            <button onclick="toggleModal('settingsModal')" class="w-full text-gray-500 mt-4 text-xs">Kapat</button>
        </div>
    </div>

    <div id="previewModal" class="fixed inset-0 bg-black z-[120] hidden flex flex-col">
        <div class="p-4 flex justify-between items-center glass"><span class="font-bold text-orange-500 text-xs">LEGENDS PREVIEW</span><button onclick="toggleModal('previewModal')" class="text-2xl">&times;</button></div>
        <iframe id="previewFrame" class="flex-1 w-full bg-white border-none"></iframe>
    </div>

    <script>
        let brain = "SOL";
        let fileText = "";

        function toggleMagic() {
            const m = document.getElementById('magic-menu');
            const b = document.getElementById('magicBtn');
            const show = m.style.display !== 'block';
            m.style.display = show ? 'block' : 'none';
            b.classList.toggle('active', show);
        }

        function setBrain(b) { brain = b; toggleMagic(); alert(b === 'SOL' ? "Legends Core Aktif" : "Local Node Aktif"); }
        function triggerFile() { document.getElementById('fileInput').click(); toggleMagic(); }
        function handleFile(input) {
            const f = input.files[0];
            const r = new FileReader();
            r.onload = (e) => { fileText = `\\n[DOSYA BAĞLAMI]:\\n${e.target.result}\\n`; alert("Dosya Hazır!"); };
            r.readAsText(f);
        }

        async function sendMsg() {
            const i = document.getElementById('userInput'); const val = i.value;
            if(!val && !fileText) return;
            if(document.getElementById('magic-menu').style.display === 'block') toggleMagic();

            addChat(val, 'user'); i.value = ""; i.style.height = 'auto';
            const id = 'ai-' + Date.now(); addLoading(id);

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val + fileText, mode: brain })
                });
                const d = await res.json();
                renderAI(id, d.answer);
                fileText = "";
            } catch(e) { renderAI(id, "❌ Bağlantı hatası!"); }
        }

        function addChat(t, type) {
            const c = document.getElementById('chat-container');
            const d = document.createElement('div'); d.className = `msg msg-${type} glass`; d.innerText = t;
            c.appendChild(d); c.scrollTop = c.scrollHeight;
        }

        function addLoading(id) {
            const c = document.getElementById('chat-container');
            const d = document.createElement('div'); d.className = `msg msg-ai glass`; d.id = id;
            d.innerHTML = `<span class="animate-pulse opacity-50">Legends AI işliyor...</span>`;
            c.appendChild(d); c.scrollTop = c.scrollHeight;
        }

        function renderAI(id, t) {
            const el = document.getElementById(id);
            el.innerHTML = `<div>${marked.parse(t)}</div>
                <div class="action-row">
                    <button onclick="copyCode('${id}')" class="act-btn"><i class="fas fa-copy"></i> KOPYALA</button>
                    <button onclick="openPreview('${id}')" class="act-btn text-orange-500"><i class="fas fa-play"></i> ÖNİZLEME</button>
                    <button onclick="appendPrompt()" class="act-btn text-blue-400"><i class="fas fa-plus"></i> GÜNCELLE</button>
                </div>`;
            document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
        }

        async function copyCode(id) {
            const el = document.getElementById(id); const codes = el.getElementsByTagName('code');
            let txt = ""; if(codes.length > 0) { for(let c of codes) txt += c.innerText + "\\n"; } else { txt = el.innerText.replace(/KOPYALA|ÖNİZLEME|GÜNCELLE/g, '').trim(); }
            await navigator.clipboard.writeText(txt); alert("Kopyalandı!");
        }

        function openPreview(id) {
            const codes = document.getElementById(id).getElementsByTagName('code');
            let s = ""; for(let c of codes) s += c.innerText + "\\n";
            document.getElementById('previewFrame').srcdoc = s;
            toggleModal('previewModal');
        }

        function appendPrompt() {
            const i = document.getElementById('userInput'); i.value = "Mevcut kodun üstüne şu özellikleri de ekle: "; i.focus();
        }

        function setTheme(name, hex) {
            document.documentElement.style.setProperty('--primary', hex);
            alert("Tema güncellendi!");
        }

        function toggleModal(id) { document.getElementById(id).classList.toggle('hidden'); }
        async function resetAI() { if(confirm("Tüm sistem resetlensin mi?")) { await fetch('/api/reset', {method:'POST'}); location.reload(); } }
        async function saveSettings() {
            await fetch('/api/settings', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({system_prompt: document.getElementById('set-prompt').value})});
            toggleModal('settingsModal'); alert("Ayarlar Kaydedildi!");
        }

        fetch('/api/settings').then(r=>r.json()).then(d=>{ document.getElementById('set-prompt').value = d.settings.system_prompt; });
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    global chat_memory, current_key_index
    data = request.json
    mode, prompt = data.get('mode', 'SOL'), data.get('prompt', '')
    chat_memory.append({"role": "user", "content": prompt})

    if mode == "SAG":
        try:
            r = requests.post("http://127.0.0.1:8080/v1/chat/completions", json={"messages": chat_memory})
            answer = r.json()['choices'][0]['message']['content']
        except: answer = "⚠️ Yerel beyin (Legends Node) uykuda."
    else:
        success = False
        while current_key_index < len(API_KEYS):
            try:
                client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=API_KEYS[current_key_index])
                res = client.chat.completions.create(model=MODEL, messages=chat_memory, temperature=SETTINGS["temperature"])
                answer = res.choices[0].message.content
                success = True; break
            except: current_key_index += 1
        if not success: answer = "❌ Limit doldu! 10 motor da yoruldu."

    if success: chat_memory.append({"role": "assistant", "content": answer})
    return jsonify({"answer": answer})

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST': SETTINGS["system_prompt"] = request.json.get("system_prompt", SETTINGS["system_prompt"])
    return jsonify({"settings": SETTINGS})

@app.route('/api/reset', methods=['POST'])
def reset(): reset_memory(); return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

