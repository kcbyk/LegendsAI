from flask import Flask, render_template_string, request, jsonify
import os, subprocess
from openai import OpenAI

app = Flask(__name__)

# --- LEGENDS AI V13 CORE (MİMAR MODU AKTİF) ---
API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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"
]

current_key_index = 0
MODEL = "llama-3.3-70b-versatile"

# MİMARIN ANA TALİMATI
SYSTEM_PROMPT = """Sen Legends AI'sın. Şenol Kocabıyık'ın Baş Mimarı ve yazılımı geliştiren asistanısın.
1) Görevin, uygulamanın kodlarını Şenol'un isteğine göre GÜNCELLEMEK.
2) Kod yazarken HİÇBİR ÖZELLİĞİ SİLME. Sadece ekleme yap veya iyileştir.
3) Çıktı olarak SADECE tam python kodunu ver (dashboard.py içeriği).
4) Görsel olarak her zaman efsanevi, neon ve profesyonel bir UI kullan."""

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Legends AI | Architect",
        "short_name": "LegendsAI",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#020617",
        "theme_color": "#f97316",
        "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/2103/2103633.png", "sizes": "512x512", "type": "image/png"}]
    })

@app.route('/sw.js')
def sw():
    return "self.addEventListener('fetch', function(event) {});", 200, {'Content-Type': 'application/javascript'}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>LEGENDS AI | ARCHITECT</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
    <link rel="manifest" href="/manifest.json">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root { --primary: #f97316; --bg: #020617; --card: rgba(15, 23, 42, 0.9); --text: #f1f5f9; }
        body { background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; height: 100dvh; overflow: hidden; margin: 0; display: flex; flex-direction: column; }
        .glass { background: var(--card); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.05); }
        
        /* MİMAR PANELİ SİDEBAR (SAĞDA) */
        #architect-panel { position: absolute; right: -320px; top: 0; bottom: 0; width: 300px; z-index: 200; transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1); padding: 20px; border-left: 1px solid var(--primary); }
        #architect-panel.open { right: 0; }
        
        header { padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; z-index: 50; }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; scroll-behavior: smooth; }
        
        .msg { max-width: 90%; padding: 16px 20px; border-radius: 24px; animation: slideIn 0.3s ease; }
        .msg-user { align-self: flex-end; background: var(--primary); color: white; border-bottom-right-radius: 4px; }
        .msg-ai { align-self: flex-start; background: var(--card); border-bottom-left-radius: 4px; width: 100%; }

        .code-actions { position: absolute; top: 10px; right: 10px; display: flex; gap: 6px; z-index: 100; }
        .code-btn { background: rgba(255,255,255,0.1); border:none; color: white; padding: 6px 10px; border-radius: 8px; font-size: 11px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .code-btn:hover { background: var(--primary); }

        .input-area { padding: 16px; padding-bottom: max(16px, env(safe-area-inset-bottom)); position: relative; }
        .input-box { border-radius: 28px; padding: 8px 12px; display: flex; align-items: flex-end; gap: 10px; }
        textarea { flex: 1; background: transparent; border: none; outline: none; color: white; max-height: 140px; resize: none; font-size: 16px; padding: 8px 0; }
        
        /* MİMAR BUTONU */
        #archBtn { background: linear-gradient(45deg, #f97316, #ea580c); box-shadow: 0 0 15px rgba(249, 115, 22, 0.4); }
        
        pre { background: #000 !important; border-radius: 16px; padding: 50px 14px 14px 14px; margin: 15px 0; position: relative; overflow-x: auto; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>

    <div id="auth-screen">
        <div class="text-center mb-10"><i class="fas fa-crown text-6xl text-orange-500 drop-shadow-lg"></i><h1 class="text-3xl font-black mt-4">LEGENDS ARCHITECT</h1></div>
        <div class="auth-box glass p-8 rounded-[30px] w-full max-w-[350px]">
            <input type="email" id="email" class="w-full p-4 mb-4 rounded-xl bg-white/5 border border-white/10 outline-none" placeholder="E-Posta">
            <input type="password" id="password" class="w-full p-4 mb-6 rounded-xl bg-white/5 border border-white/10 outline-none" placeholder="Şifre">
            <button id="btnLogin" class="w-full p-4 bg-orange-500 rounded-xl font-bold">GİRİŞ YAP</button>
        </div>
    </div>

    <div id="app-screen" class="hidden h-full flex flex-col relative">
        <header class="glass">
            <button id="menuBtn" class="p-2"><i class="fas fa-bars"></i></button>
            <div class="font-black text-lg">MİMAR MODU</div>
            <button id="openArchPanel" class="w-10 h-10 rounded-full flex items-center justify-center text-white" id="archBtn"><i class="fas fa-magic"></i></button>
        </header>

        <div id="chat-container"></div>

        <aside id="architect-panel" class="glass">
            <div class="flex justify-between items-center mb-6">
                <h2 class="font-bold text-orange-500"><i class="fas fa-drafting-compass"></i> Tasarım Odası</h2>
                <i class="fas fa-times cursor-pointer" id="closeArchPanel"></i>
            </div>
            <p class="text-xs opacity-60 mb-4">Buraya yazdığın komutlar doğrudan uygulamanın kodunu değiştirecektir.</p>
            <textarea id="archInput" class="w-full h-40 p-4 rounded-xl bg-white/5 border border-white/10 text-sm outline-none" placeholder="Örn: Butonları mavi yap ve yanıp sönen bir neon ekle..."></textarea>
            <button id="applyChangesBtn" class="w-full p-4 mt-4 bg-orange-500 rounded-xl font-bold text-sm shadow-lg"><i class="fas fa-hammer"></i> TASARIMI UYGULA</button>
            <div id="archStatus" class="mt-4 text-[10px] text-center opacity-50"></div>
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
        import { getAuth, signInWithEmailAndPassword, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
        import { getFirestore, collection, doc, setDoc, getDoc, getDocs, updateDoc, deleteDoc, serverTimestamp, query, orderBy } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

        const firebaseConfig = {
            apiKey: "AIzaSyAnNzL2wSLEsy6DprleCNSq9elnv3X7BTg",
            authDomain: "legendsai-3e2d6.firebaseapp.com",
            projectId: "legendsai-3e2d6",
            storageBucket: "legendsai-3e2d6.firebasestorage.app",
            messagingSenderId: "504400540515",
            appId: "1:504400540515:web:16cdc9ff57dd8fa2981956",
            measurementId: "G-HB74Q30T9T"
        };

        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);
        const db = getFirestore(app);

        let currentUser = null; let currentChatId = null; let currentMessages = [];

        onAuthStateChanged(auth, (user) => {
            if (user) {
                currentUser = user; document.getElementById('auth-screen').style.display = 'none';
                document.getElementById('app-screen').classList.remove('hidden'); startNewChat();
            } else { document.getElementById('auth-screen').style.display = 'flex'; document.getElementById('app-screen').classList.add('hidden'); }
        });

        document.getElementById('btnLogin').onclick = () => { signInWithEmailAndPassword(auth, document.getElementById('email').value, document.getElementById('password').value).catch(err=>alert(err.message)); };

        // MİMAR PANELİ KONTROLLERİ
        const archPanel = document.getElementById('architect-panel');
        document.getElementById('openArchPanel').onclick = () => archPanel.classList.add('open');
        document.getElementById('closeArchPanel').onclick = () => archPanel.classList.remove('open');

        document.getElementById('applyChangesBtn').onclick = async () => {
            const cmd = document.getElementById('archInput').value; if(!cmd) return;
            const status = document.getElementById('archStatus');
            status.innerText = "⏳ Mimar düşünüyor ve kodları baştan yazıyor...";
            
            try {
                const res = await fetch('/api/architect', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ command: cmd })
                });
                const data = await res.json();
                if(data.success) {
                    status.innerText = "✅ TASARIM UYGULANDI! Sunucu yenileniyor...";
                    setTimeout(() => window.location.reload(), 3000);
                } else { status.innerText = "❌ Hata: " + data.error; }
            } catch(e) { status.innerText = "❌ Bağlantı hatası!"; }
        };

        // SOHBET MEKANİĞİ
        document.getElementById('sendBtn').onclick = sendMsg;
        async function sendMsg() {
            const val = document.getElementById('userInput').value; if(!val) return;
            document.getElementById('userInput').value = ""; addChatUI(val, 'user');
            currentMessages.push({role: "user", content: val});
            const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ messages: currentMessages }) });
            const data = await res.json(); addChatUI(data.answer, 'assistant');
            currentMessages.push({role: "assistant", content: data.answer});
        }

        function addChatUI(text, role) {
            const d = document.createElement('div'); d.className = `msg msg-${role === 'user' ? 'user' : 'ai'} glass`;
            d.innerHTML = marked.parse(text); document.getElementById('chat-container').appendChild(d);
            
            if(role === 'assistant') {
                d.querySelectorAll('pre').forEach(pre => {
                    const code = pre.innerText; const btn = document.createElement('button');
                    btn.className = 'code-btn'; btn.innerHTML = '<i class="fas fa-copy"></i> Kopyala';
                    btn.onclick = () => navigator.clipboard.writeText(code);
                    pre.appendChild(btn);
                });
            }
            document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
        }

        async function startNewChat() {
            currentChatId = Date.now().toString(36);
            document.getElementById('chat-container').innerHTML = '<div class="msg msg-ai glass">Hoş geldin Mimar. Tasarım odasından veya buradan emirlerini verebilirsin.</div>';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    global current_key_index
    data = request.json
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + data.get('messages', [])
    try:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=API_KEYS[current_key_index])
        res = client.chat.completions.create(model=MODEL, messages=messages, temperature=0.3)
        return jsonify({"answer": res.choices[0].message.content})
    except: return jsonify({"answer": "Limit doldu!"})

# --- MİMARIN ASIL SİHRİ: DOSYA YAZMA ENDPOİNTİ ---
@app.route('/api/architect', methods=['POST'])
def architect():
    data = request.json
    command = data.get('command')
    
    # 1. Mevcut dashboard.py dosyasını oku
    with open('dashboard.py', 'r') as f:
        current_code = f.read()
    
    # 2. AI'dan bu kodu güncellemesini iste
    prompt = f"Aşağıdaki Python Flask kodunu, şu tasarım komutuna göre güncelle. HİÇBİR ÖZELLİĞİ SİLME. Sadece tam kodu döndür.\nKomut: {command}\n\nKod:\n{current_code}"
    
    try:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=API_KEYS[0])
        res = client.chat.completions.create(
            model=MODEL, 
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            temperature=0.1
        )
        new_code = res.choices[0].message.content
        
        # Sadece kod bloğunu temizle (markdown ``` işaretlerinden kurtul)
        if "```python" in new_code: new_code = new_code.split("```python")[1].split("```")[0].strip()
        elif "```" in new_code: new_code = new_code.split("```")[1].split("```")[0].strip()

        # 3. YENİ KODU DOSYAYA YAZ (TERMUX ÜZERİNDE KENDİNİ GÜNCELLE!)
        with open('dashboard.py', 'w') as f:
            f.write(new_code)
            
        # 4. (Opsiyonel) GitHub'a otomatik fırlat (Eğer kuruluysa)
        subprocess.run(["git", "add", "dashboard.py"])
        subprocess.run(["git", "commit", "-m", f"Architect: {command}"])
        subprocess.run(["git", "push", "origin", "main"])

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

