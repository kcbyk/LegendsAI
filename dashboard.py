from flask import Flask, render_template_string, request, jsonify
import os, subprocess
from openai import OpenAI

app = Flask(__name__)

# --- LEGENDS AI V13.5 MASTER CORE ---
API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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"
]

current_key_index = 0
MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = "Sen Legends AI'sın. Şenol Kocabıyık'ın baş yazılım mimarısın. 1) Sadece kod yaz. 2) Asla yarıda kesme. 3) Tek HTML dosyasında kusursuz iş çıkar. 4) Yazdığın kodun en altına kurulum rehberini ekle."

@app.route('/manifest.json')
def manifest():
    return jsonify({"name": "Legends AI | Master","short_name": "LegendsAI","start_url": "/","display": "standalone","background_color": "#020617","theme_color": "#f97316"})

@app.route('/sw.js')
def sw(): return "self.addEventListener('fetch', function(event) {});", 200, {'Content-Type': 'application/javascript'}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>LEGENDS AI | MASTER PRO</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root { --primary: #f97316; --bg: #020617; --card: rgba(15, 23, 42, 0.9); --text: #f1f5f9; }
        body { background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; height: 100dvh; overflow: hidden; margin: 0; display: flex; flex-direction: column; }
        .glass { background: var(--card); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.05); }
        #auth-screen { position: absolute; inset: 0; z-index: 500; display: flex; flex-direction: column; justify-content: center; align-items: center; background: var(--bg); padding: 20px; }
        #architect-panel { position: absolute; right: -320px; top: 0; bottom: 0; width: 300px; z-index: 250; transition: 0.4s; padding: 20px; border-left: 1px solid var(--primary); }
        #architect-panel.open { right: 0; }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; }
        .msg { max-width: 90%; padding: 16px 20px; border-radius: 24px; animation: slideIn 0.3s ease; }
        .msg-user { align-self: flex-end; background: var(--primary); color: white; border-bottom-right-radius: 4px; }
        .msg-ai { align-self: flex-start; background: var(--card); border: 1px solid rgba(255,255,255,0.05); width: 100%; }
        pre { background: #000 !important; border-radius: 16px; padding: 50px 14px 14px 14px; margin: 15px 0; position: relative; overflow-x: auto; border: 1px solid rgba(255,255,255,0.1); }
        .code-actions { position: absolute; top: 10px; right: 10px; display: flex; gap: 6px; z-index: 100; }
        .code-btn { background: #334155; border:none; color: white; padding: 6px 10px; border-radius: 8px; font-size: 11px; font-weight: bold; cursor: pointer; }
        .btn-upread { background: #1e3a8a; } .btn-preview { background: #14532d; }
        .input-area { padding: 16px; padding-bottom: max(16px, env(safe-area-inset-bottom)); position: relative; }
        .input-box { border-radius: 28px; padding: 8px 12px; display: flex; align-items: flex-end; gap: 10px; }
        textarea { flex: 1; background: transparent; border: none; outline: none; color: white; max-height: 140px; resize: none; font-size: 16px; padding: 8px 0; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div id="auth-screen">
        <div class="text-center mb-10"><i class="fas fa-crown text-6xl text-orange-500"></i><h1 class="text-3xl font-black mt-4">LEGENDS MASTER</h1></div>
        <div class="glass p-8 rounded-[30px] w-full max-w-[350px]">
            <input type="email" id="email" class="w-full p-4 mb-4 rounded-xl bg-white/5 border border-white/10 outline-none" placeholder="E-Posta">
            <input type="password" id="password" class="w-full p-4 mb-6 rounded-xl bg-white/5 border border-white/10 outline-none" placeholder="Şifre">
            <button id="btnLogin" class="w-full p-4 bg-orange-500 rounded-xl font-bold">GİRİŞ YAP</button>
        </div>
    </div>
    <div id="app-screen" class="hidden h-full flex flex-col relative">
        <header class="glass p-4 flex justify-between items-center">
            <button id="menuBtn"><i class="fas fa-bars"></i></button>
            <div class="font-black">LEGENDS PRO</div>
            <button id="openArchPanel" class="text-orange-500"><i class="fas fa-magic"></i></button>
        </header>
        <div id="chat-container"></div>
        <aside id="architect-panel" class="glass">
            <div class="flex justify-between items-center mb-6"><h2 class="font-bold text-orange-500">Mimar Odası</h2><i class="fas fa-times cursor-pointer" id="closeArchPanel"></i></div>
            <textarea id="archInput" class="w-full h-40 p-4 rounded-xl bg-white/5 border border-white/10 text-sm outline-none" placeholder="Tasarım emri ver..."></textarea>
            <button id="applyChangesBtn" class="w-full p-4 mt-4 bg-orange-500 rounded-xl font-bold">TASARIMI UYGULA</button>
            <div id="archStatus" class="mt-4 text-[10px] opacity-50 text-center"></div>
        </aside>
        <div class="input-area">
            <div class="input-box glass">
                <textarea id="userInput" placeholder="Yazılım emrini ver..." rows="1" oninput="this.style.height='auto';this.style.height=this.scrollHeight+'px'"></textarea>
                <div id="sendBtn" class="w-11 h-11 rounded-full bg-orange-500 flex items-center justify-center cursor-pointer flex-shrink-0"><i class="fas fa-paper-plane text-white"></i></div>
            </div>
        </div>
    </div>
    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
        import { getAuth, signInWithEmailAndPassword, onAuthStateChanged, setPersistence, browserLocalPersistence } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
        const fConfig = { apiKey: "AIzaSyAnNzL2wSLEsy6DprleCNSq9elnv3X7BTg", authDomain: "legendsai-3e2d6.firebaseapp.com", projectId: "legendsai-3e2d6", storageBucket: "legendsai-3e2d6.firebasestorage.app", messagingSenderId: "504400540515", appId: "1:504400540515:web:16cdc9ff57dd8fa2981956" };
        const app = initializeApp(fConfig); const auth = getAuth(app);
        setPersistence(auth, browserLocalPersistence);
        onAuthStateChanged(auth, (u) => { if(u){ document.getElementById('auth-screen').style.display='none'; document.getElementById('app-screen').classList.remove('hidden'); } });
        document.getElementById('btnLogin').onclick = () => { signInWithEmailAndPassword(auth, document.getElementById('email').value, document.getElementById('password').value).catch(e=>alert(e.message)); };
        document.getElementById('openArchPanel').onclick = () => document.getElementById('architect-panel').classList.add('open');
        document.getElementById('closeArchPanel').onclick = () => document.getElementById('architect-panel').classList.remove('open');
        document.getElementById('applyChangesBtn').onclick = async () => {
            const cmd = document.getElementById('archInput').value; if(!cmd) return;
            document.getElementById('archStatus').innerText = "⏳ Mimar sistemi baştan yazıyor...";
            const res = await fetch('/api/architect', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ command: cmd }) });
            const data = await res.json();
            if(data.success) { document.getElementById('archStatus').innerText = "✅ TASARIM UYGULANDI!"; setTimeout(() => window.location.reload(), 2000); } else { alert("Hata: " + data.error); }
        };
        document.getElementById('sendBtn').onclick = async () => {
            const val = document.getElementById('userInput').value; if(!val) return;
            document.getElementById('userInput').value = ""; addUI(val, 'user');
            const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ messages: [{role:"user",content:val}] }) });
            const data = await res.json(); addUI(data.answer, 'ai');
        };
        function addUI(t, r) {
            const d = document.createElement('div'); d.className = `msg msg-${r==='user'?'user':'ai'} glass`;
            d.innerHTML = marked.parse(t); document.getElementById('chat-container').appendChild(d);
            if(r==='ai') { d.querySelectorAll('pre').forEach(pre => {
                const c = pre.innerText; const acts = document.createElement('div'); acts.className = 'code-actions';
                const up = document.createElement('button'); up.className='code-btn btn-upread'; up.innerHTML='<i class="fas fa-sync"></i> Güncelle';
                up.onclick = () => { document.getElementById('userInput').value = "Şu kodu geliştir:\\n```\\n" + c + "\\n```"; };
                const cp = document.createElement('button'); cp.className='code-btn'; cp.innerHTML='<i class="fas fa-copy"></i> Kopyala';
                cp.onclick = () => { navigator.clipboard.writeText(c); cp.innerText='Alındı!'; };
                const pv = document.createElement('button'); pv.className='code-btn btn-preview'; pv.innerHTML='<i class="fas fa-play"></i> Önizle';
                pv.onclick = () => { alert('Önizleme başlatılıyor...'); };
                acts.append(up, cp, pv); pre.appendChild(acts);
            }); }
            document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    try:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=API_KEYS[0])
        res = client.chat.completions.create(model=MODEL, messages=[{"role": "system", "content": SYSTEM_PROMPT}] + data.get('messages', []), temperature=0.3)
        return jsonify({"answer": res.choices[0].message.content})
    except: return jsonify({"answer": "Limit doldu!"})

@app.route('/api/architect', methods=['POST'])
def architect():
    data = request.json
    cmd = data.get('command')
    try:
        with open('dashboard.py', 'r') as f: current = f.read()
        prompt = f"Aşağıdaki Python Flask kodunu şu tasarım komutuna göre SADECE tam kod olarak döndür: {cmd}\\n\\nKod:\\n{current}"
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=API_KEYS[0])
        res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.1)
        new_code = res.choices[0].message.content
        if "```python" in new_code: new_code = new_code.split("```python")[1].split("```")[0].strip()
        with open('dashboard.py', 'w') as f: f.write(new_code)
        subprocess.run(["git", "add", "dashboard.py"])
        subprocess.run(["git", "commit", "-m", f"Architect: {cmd}"])
        subprocess.run(["git", "push", "origin", "main"])
        return jsonify({"success": True})
    except Exception as e: return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

