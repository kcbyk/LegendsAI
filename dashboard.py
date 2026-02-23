from flask import Flask, render_template_string, request, jsonify
import requests, json, os
from openai import OpenAI

app = Flask(__name__)

# --- LEGENDS AI V10 CORE (1 MİLYON TOKEN KAPASİTESİ) ---
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
    "theme": "orange",
    "blur": 16
}

def reset_memory():
    global chat_memory
    chat_memory = [{"role": "system", "content": SETTINGS["system_prompt"]}]

reset_memory()

# --- LEGENDS AI PREMİUM UI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>LEGENDS AI | MASTER COMMAND</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root { 
            --primary: #f97316; 
            --bg: #020617; 
            --card: rgba(15, 23, 42, 0.8);
            --blur: 16px;
        }
        body { background: var(--bg); color: #f1f5f9; font-family: 'Inter', system-ui, sans-serif; height: 100dvh; display: flex; flex-direction: column; overflow: hidden; margin: 0; }
        
        .glass { background: var(--card); backdrop-filter: blur(var(--blur)); border: 1px solid rgba(255, 255, 255, 0.08); }
        .neon-glow { box-shadow: 0 0 20px rgba(249, 115, 22, 0.15); }

        header { padding: 18px 24px; display: flex; justify-content: space-between; align-items: center; z-index: 50; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .logo { font-weight: 900; letter-spacing: -1px; font-size: 1.4rem; display: flex; align-items: center; gap: 10px; }
        .logo i { color: var(--primary); filter: drop-shadow(0 0 8px var(--primary)); }

        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; }
        .msg { max-width: 92%; padding: 16px 20px; border-radius: 24px; line-height: 1.6; font-size: 15px; position: relative; }
        .msg-user { align-self: flex-end; background: linear-gradient(135deg, var(--primary), #ea580c); color: white; border-bottom-right-radius: 4px; box-shadow: 0 4px 15px rgba(249, 115, 22, 0.2); }
        .msg-ai { align-self: flex-start; background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.05); border-bottom-left-radius: 4px; width: 100%; }
        
        #magic-menu { display: none; position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); width: 92%; max-width: 450px; z-index: 100; border-radius: 32px; padding: 12px; animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .menu-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
        .menu-item { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 18px; border-radius: 20px; background: rgba(255,255,255,0.03); transition: 0.3s; cursor: pointer; border: 1px solid transparent; }
        .menu-item:active { background: rgba(255,255,255,0.08); border-color: var(--primary); transform: scale(0.95); }
        .menu-item i { font-size: 1.6rem; }

        .input-area { padding: 16px; padding-bottom: max(16px, env(safe-area-inset-bottom)); z-index: 60; }
        .input-box { border-radius: 28px; padding: 8px 8px 8px 20px; display: flex; align-items: flex-end; gap: 12px; transition: 0.3s; }
        .input-box:focus-within { border-color: var(--primary); box-shadow: 0 0 15px rgba(249, 115, 22, 0.1); }
        textarea { flex: 1; background: transparent; border: none; outline: none; color: white; padding: 10px 0; max-height: 150px; resize: none; font-size: 16px; }
        
        .circle-btn { width: 48px; height: 48px; border-radius: 50%; display: flex; justify-content: center; align-items: center; transition: 0.3s; cursor: pointer; }
        .btn-magic { background: rgba(255,255,255,0.05); color: #94a3b8; }
        .btn-magic.active { transform: rotate(45deg); background: var(--primary); color: white; }
        .btn-send { background: var(--primary); color: white; box-shadow: 0 6px 20px rgba(249, 115, 22, 0.3); }

        /* Action Buttons */
        .action-row { display: flex; gap: 8px; margin-top: 15px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.05); flex-wrap: wrap; }
        .act-btn { padding: 8px 16px; border-radius: 12px; font-size: 11px; font-weight: 700; display: flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.04); transition: 0.2s; border: 1px solid rgba(255,255,255,0.05); }
        .act-btn:active { background: var(--primary); color: white; }

        pre { background: #000 !important; border-radius: 16px; padding: 16px; margin: 12px 0; overflow-x: auto; border: 1px solid rgba(255,255,255,0.08); }
        code { font-family: 'Fira Code', 'Consolas', monospace; font-size: 13px; color: #e2e8f0; }
        
        @keyframes slideUp { from { opacity: 0; transform: translate(-50%, 20px); } to { opacity: 1; transform: translate(-50%, 0); } }
    </style>
</head>
<body data-theme="orange">

    <header class="glass">
        <div class="logo"><i class="fas fa-bolt"></i> LEGENDS AI</div>
        <div class="flex gap-4">
            <button onclick="toggleModal('settingsModal')" class="text-gray-400 text-xl"><i class="fas fa-terminal"></i></button>
        </div>
    </header>

    <div id="chat-container">
        <div class="msg msg-ai glass">
            <b>Legends AI Core:</b> Sistem başlatıldı. 10 Motor (V10) %100 kapasiteyle çalışıyor. Bugün neyi baştan yaratıyoruz patron?
        </div>
    </div>

    <div id="magic-menu" class="glass neon-glow">
        <div class="menu-grid">
            <div class="menu-item" onclick="setBrain('SOL')">
                <i class="fas fa-cloud-bolt text-orange-500"></i>
                <span class="text-[10px] font-black uppercase">Legends Core</span>
            </div>
            <div class="menu-item" onclick="setBrain('SAG')">
                <i class="fas fa-microchip text-blue-500"></i>
                <span class="text-[10px] font-black uppercase">Local Node</span>
            </div>
            <div class="menu-item" onclick="triggerFile()">
                <i class="fas fa-folder-open text-purple-500"></i>
                <span class="text-[10px] font-black uppercase">Dosya Ekle</span>
            </div>
            <div class="menu-item" onclick="alert('Görsel Analiz v2 Çok Yakında!')">
                <i class="fas fa-eye text-green-500"></i>
                <span class="text-[10px] font-black uppercase">Fotoğraf</span>
            </div>
            <div class="menu-item" onclick="resetAI()">
                <i class="fas fa-trash-can text-red-500"></i>
                <span class="text-[10px] font-black uppercase">Hafızayı Sil</span>
            </div>
            <div class="menu-item" onclick="toggleModal('settingsModal')">
                <i class="fas fa-sliders text-gray-400"></i>
                <span class="text-[10px] font-black uppercase">Ayarlar</span>
            </div>
        </div>
    </div>

    <div class="input-area">
        <div class="input-box glass">
            <div id="magicBtn" onclick="toggleMagic()" class="circle-btn btn-magic"><i class="fas fa-plus"></i></div>
            <textarea id="userInput" placeholder="Mesajınızı buraya bırakın..." rows="1" oninput="autoHeight(this)"></textarea>
            <div onclick="sendMsg()" class="circle-btn btn-send"><i class="fas fa-paper-plane"></i></div>
        </div>
    </div>

    <input type="file" id="fileInput" class="hidden" onchange="processFile(this)">

    <div id="settingsModal" class="fixed inset-0 bg-black/90 z-[110] hidden flex items-center justify-center p-4 backdrop-blur-md">
        <div class="glass w-full max-w-md rounded-[40px] p-8 border-t-2 border-orange-500/30">
            <h2 class="text-2xl font-black mb-6 flex items-center gap-3">
                <i class="fas fa-cog text-orange-500"></i> KOMUTA MERKEZİ
            </h2>
            
            <div class="space-y-6">
                <div>
                    <label class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 block">Sistem Komutu</label>
                    <textarea id="set-prompt" class="w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-sm h-32 text-white outline-none focus:border-orange-500"></textarea>
                </div>
                
                <div>
                    <label class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 block">Yaratıcılık Düzeyi (Temp)</label>
                    <input type="range" id="set-temp" min="0" max="100" class="w-full accent-orange-500">
                </div>

                <div>
                    <label class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 block">Arayüz Teması</label>
                    <div class="flex gap-3">
                        <div onclick="setTheme('orange', '#f97316')" class="w-10 h-10 rounded-full bg-orange-500 cursor-pointer border-2 border-white/20"></div>
                        <div onclick="setTheme('blue', '#3b82f6')" class="w-10 h-10 rounded-full bg-blue-500 cursor-pointer"></div>
                        <div onclick="setTheme('green', '#22c55e')" class="w-10 h-10 rounded-full bg-green-500 cursor-pointer"></div>
                        <div onclick="setTheme('purple', '#a855f7')" class="w-10 h-10 rounded-full bg-purple-500 cursor-pointer"></div>
                    </div>
                </div>
            </div>

            <div class="flex gap-4 mt-8">
                <button onclick="toggleModal('settingsModal')" class="flex-1 bg-white/5 py-4 rounded-2xl font-bold">KAPAT</button>
                <button onclick="saveSettings()" class="flex-1 bg-orange-600 py-4 rounded-2xl font-bold shadow-lg shadow-orange-900/40">GÜNCELLE</button>
            </div>
        </div>
    </div>

    <div id="previewModal" class="fixed inset-0 bg-[#000] z-[120] hidden flex flex-col">
        <div class="p-4 flex justify-between items-center bg-[#111] border-b border-white/10">
            <div class="text-xs font-black text-orange-500 uppercase">Legends AI Preview</div>
            <button onclick="toggleModal('previewModal')" class="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center"><i class="fas fa-times"></i></button>
        </div>
        <iframe id="previewFrame" class="flex-1 w-full bg-white border-none"></iframe>
    </div>

    <script>
        let brain = "SOL";
        let fileData = "";

        function toggleMagic() {
            const m = document.getElementById('magic-menu');
            const b = document.getElementById('magicBtn');
            const show = m.style.display !== 'block';
            m.style.display = show ? 'block' : 'none';
            b.classList.toggle('active', show);
        }

        function setBrain(b) { brain = b; alert(`Motor Değişti: ${b === 'SOL' ? 'Legends Cloud' : 'Local Node'}`); toggleMagic(); }
        function triggerFile() { document.getElementById('fileInput').click(); toggleMagic(); }
        
        function processFile(input) {
            const f = input.files[0];
            const r = new FileReader();
            r.onload = (e) => { fileData = `\\n[BAĞLAM DOSYASI]:\\n${e.target.result}\\n`; alert("Dosya Entegre Edildi!"); };
            r.readAsText(f);
        }

        async function sendMsg() {
            const input = document.getElementById('userInput');
            const val = input.value;
            if(!val && !fileData) return;
            if(document.getElementById('magic-menu').style.display === 'block') toggleMagic();

            addChat(val, 'user');
            input.value = ""; input.style.height = 'auto';
            const id = 'msg-' + Date.now();
            addLoading(id);

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val + fileData, mode: brain })
                });
                const d = await res.json();
                renderResponse(id, d.answer);
                fileData = "";
            } catch(e) { renderResponse(id, "❌ Komuta merkezi ile bağlantı kesildi!"); }
        }

        function addChat(text, type) {
            const c = document.getElementById('chat-container');
            const d = document.createElement('div');
            d.className = `msg msg-${type} glass`;
            d.innerText = text;
            c.appendChild(d);
            c.scrollTop = c.scrollHeight;
        }

        function addLoading(id) {
            const c = document.getElementById('chat-container');
            const d = document.createElement('div');
            d.className = `msg msg-ai glass`; d.id = id;
            d.innerHTML = `<span class="opacity-50 italic">Legends AI Core verileri işliyor...</span>`;
            c.appendChild(d);
            c.scrollTop = c.scrollHeight;
        }

        function renderResponse(id, text) {
            const el = document.getElementById(id);
            el.innerHTML = `<div>${marked.parse(text)}</div>
                <div class="action-row">
                    <button onclick="copyContent('${id}')" class="act-btn"><i class="fas fa-copy"></i> KOPYALA</button>
                    <button onclick="openPreview('${id}')" class="act-btn text-orange-500"><i class="fas fa-play"></i> ÖNİZLEME</button>
                    <button onclick="appendPrompt('${id}')" class="act-btn text-blue-400"><i class="fas fa-plus"></i> GÜNCELLE</button>
                </div>`;
            document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
        }

        async function copyContent(id) {
            const el = document.getElementById(id);
            const codes = el.getElementsByTagName('code');
            let txt = "";
            if(codes.length > 0) { for(let c of codes) txt += c.innerText + "\\n"; }
            else { txt = el.innerText.replace(/KOPYALA|ÖNİZLEME|GÜNCELLE/g, '').trim(); }
            
            try {
                await navigator.clipboard.writeText(txt);
                alert("✅ İçerik panoya kopyalandı!");
            } catch(err) {
                const ta = document.createElement("textarea");
                ta.value = txt; document.body.appendChild(ta);
                ta.select(); document.execCommand("copy");
                document.body.removeChild(ta);
                alert("✅ Kopyalandı (Yedek Metod)");
            }
        }

        function openPreview(id) {
            const codes = document.getElementById(id).getElementsByTagName('code');
            let s = ""; for(let c of codes) s += c.innerText + "\\n";
            if(!s.includes('<html')) { alert("Bu mesajda önizlenebilir bir HTML kodu bulunamadı!"); return; }
            document.getElementById('previewFrame').srcdoc = s;
            toggleModal('previewModal');
        }

        function appendPrompt() {
            const i = document.getElementById('userInput');
            i.value = "Mevcut kodun üstüne şu özellikleri de ekle: ";
            i.focus();
        }

        function setTheme(name, hex) {
            document.documentElement.style.setProperty('--primary', hex);
            alert(`Tema güncellendi: ${name.toUpperCase()}`);
        }

        function autoHeight(el) { el.style.height = 'auto'; el.style.height = el.scrollHeight + 'px'; }
        function toggleModal(id) { document.getElementById(id).classList.toggle('hidden'); }
        async function resetAI() { if(confirm("Tüm hafıza ve sistem resetlensin mi?")) { await fetch('/api/reset', {method:'POST'}); location.reload(); } }
        
        async function saveSettings() {
            const p = document.getElementById('set-prompt').value;
            const t = document.getElementById('set-temp').value / 100;
            await fetch('/api/settings', {
                method:'POST', 
                headers:{'Content-Type':'application/json'}, 
                body:JSON.stringify({system_prompt: p, temperature: t})
            });
            toggleModal('settingsModal');
            alert("Sistem Parametreleri Güncellendi!");
        }

        // Başlangıç ayarlarını yükle
        fetch('/api/settings').then(r=>r.json()).then(d=>{
            document.getElementById('set-prompt').value = d.settings.system_prompt;
            document.getElementById('set-temp').value = d.settings.temperature * 100;
        });
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
        except: answer = "⚠️ Yerel beyin şu an ulaşılamaz durumda."
    else:
        success = False
        while current_key_index < len(API_KEYS):
            try:
                client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=API_KEYS[current_key_index])
                res = client.chat.completions.create(model=MODEL, messages=chat_memory, temperature=SETTINGS["temperature"])
                answer = res.choices[0].message.content
                success = True; break
            except: current_key_index += 1
        if not success: answer = "❌ Tüm Legends Core motorları tükendi! Yeni kotalar için gece 03:00'ü bekleyin."

    if success: chat_memory.append({"role": "assistant", "content": answer})
    return jsonify({"answer": answer})

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        SETTINGS["system_prompt"] = request.json.get("system_prompt", SETTINGS["system_prompt"])
        SETTINGS["temperature"] = float(request.json.get("temperature", SETTINGS["temperature"]))
    return jsonify({"settings": SETTINGS})

@app.route('/api/reset', methods=['POST'])
def reset(): reset_memory(); return jsonify({"status": "ok"})

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=False)

