from flask import Flask, render_template_string, request, jsonify
import os
import requests

app = Flask(__name__)

# --- 7️⃣ TEKNİK MİMARİ: 10 ANAHTARLI HATA TOLERANSLI MOTOR ---
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
    
    # AI Plus Seviyesinde Sistem Talimatı
    sys_prompt = {"role": "system", "content": "Sen Legends Master Pro v26'sın. Şenol Kocabıyık'ın (19) baş mimarısın. Her yazılımı profesyonelce yazar, adım adım öğretirsin. v1/v2/v3 versiyonlama yaparsın."}
    full_messages = [sys_prompt] + messages

    attempts = 0
    while attempts < len(API_KEYS):
        try:
            # Doğrudan Groq API çağrısı (Kütüphane hatalarını önlemek için)
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEYS[current_key_index]}", "Content-Type": "application/json"},
                json={"model": MODEL, "messages": full_messages, "temperature": temp, "max_tokens": 4096},
                timeout=20
            )
            if resp.status_code == 200:
                return jsonify({"answer": resp.json()['choices'][0]['message']['content']})
            else:
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                attempts += 1
        except Exception:
            current_key_index = (current_key_index + 1) % len(API_KEYS)
            attempts += 1
            
    return jsonify({"answer": "❌ Sunucu meşgul patron, anahtarları kontrol ediyorum..."})

# --- 8 MADDELİK ANAYASANIN TÜRKÇE VE MÜKEMMEL ARAYÜZÜ ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
    <meta charset="UTF-8">
    <title>Legends Master Pro | v26.0 Ultimate</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root { --bg: #000; --panel: #0a0a0a; --border: #1a1a1a; --primary: #fff; }
        body { background: var(--bg); color: #fff; font-family: -apple-system, sans-serif; height: 100dvh; display: flex; overflow: hidden; }
        
        /* 2️⃣ ANA PANEL & 5️⃣ SIDEBAR */
        .sidebar { width: 300px; background: #000; border-right: 1px solid var(--border); transition: 0.3s; display: flex; flex-direction: column; }
        .sidebar-item { padding: 12px; border-radius: 12px; cursor: pointer; transition: 0.2s; font-size: 13px; color: #888; border: 1px solid transparent; }
        .sidebar-item:hover { background: #111; color: #fff; border-color: #222; }
        .sidebar-item.active { background: #111; color: #fff; border-color: #333; }

        /* 3️⃣ SOHBET SİSTEMİ & 8️⃣ ANİMASYONLAR */
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; scroll-behavior: smooth; }
        .msg-user { background: #111; border: 1px solid var(--border); border-radius: 16px; padding: 14px 18px; margin: 8px 0 8px auto; max-width: 85%; animation: slideUp 0.3s ease; }
        .msg-ai { padding: 24px 0; border-bottom: 1px solid #0f0f0f; display: flex; gap: 16px; animation: slideUp 0.4s ease; }
        .avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; }
        
        /* 4️⃣ VERSİYONLAMA, KOPYALAMA & ÖNİZLEME BUTONLARI */
        pre { background: #050505 !important; border: 1px solid var(--border); border-radius: 12px; padding: 50px 16px 16px 16px; margin: 16px 0; position: relative; overflow-x: auto; }
        .code-header { position: absolute; top: 12px; right: 12px; display: flex; gap: 8px; opacity: 0; transition: 0.3s; }
        pre:hover .code-header { opacity: 1; }
        .code-btn { padding: 6px 12px; border-radius: 8px; font-size: 11px; font-weight: bold; cursor: pointer; border: 1px solid #333; color: #fff; transition: 0.2s; }
        .btn-v2 { background: #2563eb; } .btn-pre { background: #16a34a; }
        
        .typing { display: flex; gap: 4px; padding-top: 8px; }
        .dot { width: 4px; height: 4px; background: #555; border-radius: 50%; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
        
        .modal { display: none; position: fixed; inset: 0; z-index: 9999; background: rgba(0,0,0,0.9); align-items: center; justify-content: center; backdrop-filter: blur(20px); }
        .modal.active { display: flex; }
        @media (max-width: 768px) { .sidebar { position: absolute; transform: translateX(-100%); z-index: 5000; height: 100%; } .sidebar.open { transform: translateX(0); } }
    </style>
</head>
<body>

    <div id="auth-screen" class="fixed inset-0 z-[10000] bg-black flex items-center justify-center p-6">
        <div class="border border-[#1a1a1a] bg-[#050505] p-12 rounded-[40px] w-full max-w-sm text-center shadow-2xl">
            <i class="fas fa-cube text-6xl mb-10"></i>
            <h1 class="text-3xl font-black mb-10 tracking-tighter">LEGENDS PRO</h1>
            <div class="space-y-4 mb-8">
                <input type="email" id="authEmail" class="w-full p-4 rounded-2xl bg-[#111] border border-[#222] text-sm focus:border-white outline-none transition" placeholder="Email">
                <input type="password" id="authPass" class="w-full p-4 rounded-2xl bg-[#111] border border-[#222] text-sm focus:border-white outline-none transition" placeholder="Şifre">
            </div>
            <button id="btnLogin" class="w-full p-4 bg-white text-black rounded-2xl font-bold mb-4 hover:scale-105 transition">Giriş Yap</button>
            <button id="btnGoogle" class="w-full p-4 bg-[#111] border border-[#222] rounded-2xl font-bold flex items-center justify-center gap-2 text-xs transition active:scale-95"><i class="fab fa-google"></i> Google ile Devam Et</button>
        </div>
    </div>

    <aside id="sidebar" class="sidebar">
        <div class="p-6 border-b border-[#1a1a1a] flex justify-between items-center"><span class="font-black text-lg tracking-tighter">LEGENDS ARCHITECT</span><i class="fas fa-times md:hidden" id="closeSidebar"></i></div>
        <div class="p-4"><button id="newChatBtn" class="w-full p-4 bg-[#111] border border-[#222] rounded-2xl text-xs font-bold hover:bg-white hover:text-black transition flex items-center justify-center gap-2"><i class="fas fa-plus"></i> YENİ PROJE</button></div>
        <div id="historyList" class="flex-1 overflow-y-auto px-4 space-y-2"></div>
        <div class="p-6 border-t border-[#1a1a1a] flex items-center justify-between">
            <div class="flex items-center gap-3"><div class="avatar bg-white text-black text-xs">ŞK</div><span class="font-bold text-xs" id="uName">Patron</span></div>
            <i class="fas fa-cog text-gray-600 cursor-pointer hover:text-white" id="openSettings"></i>
        </div>
    </aside>

    <main class="flex-1 flex flex-col relative h-full">
        <header class="h-16 border-b border-[#0a0a0a] flex items-center px-6 md:hidden"><i class="fas fa-bars mr-4 text-xl" id="openSidebar"></i><span class="font-bold">LEGENDS PRO</span></header>
        <div id="chat-container">
            <div class="h-full flex flex-col items-center justify-center text-white opacity-10 select-none pt-40"><i class="fas fa-cube text-8xl mb-6"></i><p class="font-black tracking-[0.5em] text-sm">V26.0 MASTER</p></div>
        </div>

        <div class="p-6 md:p-12 bg-gradient-to-t from-black via-black to-transparent">
            <div class="max-w-4xl mx-auto bg-[#0a0a0a] border border-[#1a1a1a] rounded-[28px] p-2 flex items-end gap-2 focus-within:border-[#333] transition-all shadow-2xl">
                <button class="p-4 text-gray-500 hover:text-white transition"><i class="fas fa-paperclip text-lg"></i></button>
                <textarea id="userInput" class="flex-1 bg-transparent border-none text-white py-4 text-sm outline-none resize-none max-h-[200px]" placeholder="Mimar için bir emir yaz..." rows="1"></textarea>
                <button id="sendBtn" class="p-4 bg-white text-black rounded-2xl font-black hover:scale-105 active:scale-95 transition-all"><i class="fas fa-arrow-up"></i></button>
            </div>
        </div>
    </main>

    <div id="settingsModal" class="modal">
        <div class="bg-[#050505] border border-[#1a1a1a] p-10 rounded-[40px] w-full max-w-md">
            <div class="flex justify-between items-center mb-10 font-black"><span>SİSTEM KONTROLÜ</span><i class="fas fa-times cursor-pointer" id="closeSettings"></i></div>
            <div class="space-y-8">
                <div><label class="flex justify-between text-[10px] text-gray-500 font-black mb-4 uppercase"><span>AI Sıcaklığı</span><span id="tVal">0.2</span></label>
                <input type="range" id="tRange" min="0" max="1" step="0.1" value="0.2" class="w-full accent-white h-1 bg-[#1a1a1a] appearance-none rounded-full"></div>
                <div class="p-8 bg-[#0a0a0a] border border-[#1a1a1a] rounded-3xl text-center"><h3 class="font-black text-xs mb-3 text-blue-500">AI ÖZEL EĞİTİM</h3><p class="text-[10px] text-gray-500 mb-6">Proje dosyalarını yükle, sistem analiz etsin.</p><button class="w-full p-4 bg-white text-black rounded-2xl text-xs font-bold">VERİ YÜKLE</button></div>
                <button id="btnLogout" class="w-full p-4 border border-red-900/50 text-red-500 rounded-2xl text-xs font-black">OTURUMU KAPAT</button>
            </div>
        </div>
    </div>

    <div id="previewModal" class="modal">
        <div class="bg-black border border-[#1a1a1a] w-[98%] h-[95vh] rounded-[32px] overflow-hidden flex flex-col shadow-2xl">
            <div class="p-5 flex justify-between items-center bg-[#050505] border-b border-[#1a1a1a]"><span class="text-[10px] font-black text-gray-500 tracking-widest uppercase">Legends Live Preview</span><i class="fas fa-times cursor-pointer text-gray-500" id="closePreview"></i></div>
            <iframe id="pFrame" class="flex-1 w-full bg-white" sandbox="allow-scripts"></iframe>
        </div>
    </div>

    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
        import { getAuth, signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut, setPersistence, browserLocalPersistence } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
        import { getFirestore, collection, doc, setDoc, getDoc, updateDoc, deleteDoc, query, orderBy, onSnapshot, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

        const fConfig = { apiKey: "AIzaSyAnNzL2wSLEsy6DprleCNSq9elnv3X7BTg", authDomain: "legendsai-3e2d6.firebaseapp.com", projectId: "legendsai-3e2d6", storageBucket: "legendsai-3e2d6.firebasestorage.app", messagingSenderId: "504400540515", appId: "1:504400540515:web:16cdc9ff57dd8fa2981956" };
        const app = initializeApp(fConfig); const auth = getAuth(app); const db = getFirestore(app);
        setPersistence(auth, browserLocalPersistence);

        let cUser = null, cChatId = null, history = [], config = { temperature: 0.2 };

        // [object Object] HATASINI ÇÖZEN VE ÖNİZLEMEYİ TETİKLEYEN RENDERER
        const renderer = new marked.Renderer();
        renderer.code = function(code, lang) {
            const rawCode = typeof code === 'object' ? code.text : String(code);
            const escaped = rawCode.replace(/`/g, '\\`').replace(/'/g, "\\'").replace(/"/g, '&quot;');
            
            // index.html VEYA HTML İÇERİĞİNDE ÖNİZLEME BUTONU AKTİF OLSUN
            const isHTML = (lang === 'html' || rawCode.toLowerCase().includes('<!doctype') || rawCode.toLowerCase().includes('<html>'));
            
            return `<div class="relative group">
                <div class="code-header">
                    <button onclick="window.uCode(\`${escaped}\`)" class="code-btn btn-v2">GÜNCELLE v2</button>
                    <button onclick="window.cCode(\`${escaped}\`, this)" class="code-btn">KOPYALA</button>
                    ${isHTML ? `<button onclick="window.pCode(\`${escaped}\`)" class="code-btn btn-pre">ÖNİZLE</button>` : ''}
                </div>
                <pre><code class="language-${lang}">${rawCode}</code></pre>
            </div>`;
        };
        marked.setOptions({ renderer: renderer });

        window.uCode = (c) => { document.getElementById('userInput').value = `Bu kodu geliştirerek v2 sürümünü yap:\\n\\n\`\`\`\\n${c}\`\`\``; document.getElementById('userInput').focus(); };
        window.cCode = (c, b) => { navigator.clipboard.writeText(c); b.innerText = 'BİTTİ'; setTimeout(()=>b.innerText='KOPYALA', 2000); };
        window.pCode = (c) => { document.getElementById('previewModal').classList.add('active'); document.getElementById('pFrame').srcdoc = c; };

        onAuthStateChanged(auth, (u) => {
            if(u){
                cUser = u; document.getElementById('auth-screen').style.display = 'none';
                document.getElementById('uName').innerText = u.email.split('@')[0].toUpperCase();
                syncH(); startN();
            } else { document.getElementById('auth-screen').style.display = 'flex'; }
        });

        document.getElementById('btnLogin').onclick = () => signInWithEmailAndPassword(auth, document.getElementById('authEmail').value, document.getElementById('authPass').value).catch(e => alert(e.message));
        document.getElementById('btnGoogle').onclick = () => signInWithPopup(auth, new GoogleAuthProvider());
        document.getElementById('btnLogout').onclick = () => { signOut(auth); document.getElementById('settingsModal').classList.remove('active'); };

        function syncH() {
            const q = query(collection(db, `users/${cUser.uid}/chats`), orderBy('updatedAt', 'desc'));
            onSnapshot(q, (s) => {
                const l = document.getElementById('historyList'); l.innerHTML = "";
                s.forEach(d => {
                    const active = cChatId === d.id;
                    const div = document.createElement('div');
                    div.className = `sidebar-item ${active ? 'active' : ''}`;
                    div.innerHTML = `<div class="flex justify-between items-center"><span class="truncate pr-2 font-bold uppercase tracking-tighter">${d.data().title || 'Yeni Proje'}</span><i class="fas fa-trash-alt opacity-0 group-hover:opacity-40" onclick="event.stopPropagation(); window.delC('${d.id}')"></i></div>`;
                    div.onclick = () => loadC(d.id); l.appendChild(div);
                });
            });
        }

async function startN() {
            cChatId = "chat_" + Date.now(); history = [];
            document.getElementById('chat-container').innerHTML = '<div class="h-full flex flex-col items-center justify-center text-white opacity-10 select-none pt-40"><i class="fas fa-cube text-8xl mb-6"></i><p class="font-black tracking-[0.5em] text-sm uppercase">V26.0 MASTER ARCHITECT</p></div>';
            await setDoc(doc(db, `users/${cUser.uid}/chats`, cChatId), { title: "Yeni Proje", updatedAt: serverTimestamp(), messages: [] });
        }

        async function loadC(id) {
            cChatId = id; const d = await getDoc(doc(db, `users/${cUser.uid}/chats`, id));
            if(d.exists()){ history = d.data().messages || []; renderC(); }
        }
        window.delC = async (id) => { if(confirm("Silinsin mi patron?")) { await deleteDoc(doc(db, `users/${cUser.uid}/chats`, id)); startN(); } };

        document.getElementById('sendBtn').onclick = sendM;
        document.getElementById('userInput').oninput = function() { this.style.height = 'auto'; this.style.height = this.scrollHeight + 'px'; };
        document.getElementById('userInput').onkeydown = (e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendM(); } };

        async function sendM() {
            const v = document.getElementById('userInput').value.trim(); if(!v) return;
            if(history.length === 0) document.getElementById('chat-container').innerHTML = '';
            
            document.getElementById('userInput').value = ""; document.getElementById('userInput').style.height = 'auto';
            addUI(v, 'user'); history.push({role: "user", content: v});
            
            const lId = "ai_" + Date.now();
            document.getElementById('chat-container').innerHTML += `<div id="${lId}" class="msg-ai"><div class="avatar bg-white text-black text-xs">ŞK</div><div class="typing"><div class="dot"></div><div class="dot" style="animation-delay:0.2s"></div><div class="dot" style="animation-delay:0.4s"></div><span class="ml-4 text-[10px] font-black uppercase tracking-widest text-gray-600">Mimar İnşa Ediyor...</span></div></div>`;
            document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;

            try {
                const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ messages: history, settings: config }) });
                const d = await res.json();
                document.getElementById(lId).remove();
                addUI(d.answer, 'assistant'); history.push({role: "assistant", content: d.answer});
                await updateDoc(doc(db, `users/${cUser.uid}/chats`, cChatId), { title: history[0].content.substring(0, 30), messages: history, updatedAt: serverTimestamp() });
            } catch(e) { document.getElementById(lId).innerHTML = "❌ BAĞLANTI HATASI"; }
        }

        function addUI(t, r) {
            const d = document.createElement('div'); d.className = r === 'user' ? 'msg-user' : 'msg-ai';
            if(r === 'user') d.innerText = t;
            else d.innerHTML = `<div class="avatar bg-white text-black text-xs shadow-lg shadow-white/5">ŞK</div><div class="flex-1 overflow-hidden markdown-body text-gray-200">${marked.parse(t)}</div>`;
            document.getElementById('chat-container').appendChild(d);
            document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
        }
        function renderC() { document.getElementById('chat-container').innerHTML = ""; history.forEach(m => addUI(m.content, m.role)); }

        document.getElementById('openSidebar').onclick = () => document.getElementById('sidebar').classList.add('open');
        document.getElementById('closeSidebar').onclick = () => document.getElementById('sidebar').classList.remove('open');
        document.getElementById('newChatBtn').onclick = startN;
        document.getElementById('openSettings').onclick = () => document.getElementById('settingsModal').classList.add('active');
        document.getElementById('closeSettings').onclick = () => document.getElementById('settingsModal').classList.remove('active');
        document.getElementById('closePreview').onclick = () => document.getElementById('previewModal').classList.remove('active');
        document.getElementById('tRange').oninput = (e) => { document.getElementById('tVal').innerText = e.target.value; config.temperature = parseFloat(e.target.value); };
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
