from flask import Flask, render_template_string, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# --- 7️⃣ TEKNİK MİMARİ: 10 KEY GROQ ENGINE ---
API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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"
]
current_key_index = 0
MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = """Sen Legends Master Pro v23'sün. Şenol Kocabıyık'ın (19) baş mimarısın.
1) Kod üretiminde v1, v2 versiyonlama mantığını kullan.
2) Güncelle butonu için kodları merge ederek iyileştir.
3) Arayüz her zaman premium siyah (dark) olmalı."""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    global current_key_index
    data = request.json
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + data.get('messages', [])
    temp = data.get('settings', {}).get('temperature', 0.2)
    attempts = 0
    while attempts < len(API_KEYS):
        try:
            client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=API_KEYS[current_key_index])
            res = client.chat.completions.create(model=MODEL, messages=messages, temperature=temp)
            return jsonify({"answer": res.choices[0].message.content})
        except Exception:
            current_key_index = (current_key_index + 1) % len(API_KEYS)
            attempts += 1
    return jsonify({"answer": "❌ Limit doldu patron, anahtar değiştiriliyor..."})

# --- 500 SATIRLIK EFSANEVİ 8 MADDELİK ARAYÜZ ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
    <meta charset="UTF-8">
    <title>Legends Master Pro v23</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root { --bg: #000000; --card: #0A0A0A; --border: #222; --primary: #ffffff; }
        body { background: var(--bg); color: #fff; font-family: -apple-system, sans-serif; height: 100dvh; display: flex; overflow: hidden; }
        
        /* 2️⃣ ANA PANEL YAPISI */
        .sidebar { width: 280px; background: #000; border-right: 1px solid var(--border); transition: 0.3s; display: flex; flex-direction: column; }
        .msg-user { background: #111; border: 1px solid var(--border); border-radius: 12px; padding: 14px; margin: 8px 0 8px auto; max-width: 85%; font-size: 14px; }
        .msg-ai { padding: 16px 0; border-bottom: 1px solid #111; display: flex; gap: 14px; font-size: 14px; }
        
        /* 4️⃣ GÜNCELLEME SİSTEMİ & KOD BLOKLARI */
        pre { background: #050505 !important; border: 1px solid var(--border); border-radius: 10px; padding: 50px 16px 16px 16px; margin: 16px 0; position: relative; overflow-x: auto; color: #ccc; }
        .code-header { position: absolute; top: 12px; right: 12px; display: flex; gap: 6px; opacity: 0; transition: 0.2s; }
        pre:hover .code-header { opacity: 1; }
        .code-btn { padding: 5px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; border: 1px solid var(--border); color: #fff; cursor: pointer; transition: 0.2s; }
        .btn-v2 { background: #2563eb; } .btn-pre { background: #16a34a; }
        
        /* 8️⃣ EKSTRA ÖZELLİKLER */
        .modal { display: none; position: fixed; inset: 0; z-index: 9999; background: rgba(0,0,0,0.95); align-items: center; justify-content: center; padding: 20px; backdrop-filter: blur(15px); }
        .modal.active { display: flex; }
        .typing { width: 4px; height: 4px; background: #fff; border-radius: 50%; animation: blink 1s infinite; display: inline-block; margin: 0 1px; }
        @keyframes blink { 0%, 100% { opacity: 0.2; } 50% { opacity: 1; } }
        @media (max-width: 768px) { .sidebar { position: absolute; transform: translateX(-100%); z-index: 5000; height: 100%; } .sidebar.open { transform: translateX(0); } }
    </style>
</head>
<body>

    <div id="auth-screen" class="fixed inset-0 z-[10000] bg-black flex items-center justify-center p-6">
        <div class="border border-[#333] bg-[#050505] p-10 rounded-2xl w-full max-w-sm text-center">
            <i class="fas fa-cube text-5xl mb-8"></i>
            <h1 class="text-xl font-bold mb-8">LEGENDS MASTER PRO</h1>
            <div class="space-y-4 mb-6">
                <input type="email" id="authEmail" class="w-full p-4 rounded-xl bg-[#111] border border-[#222] text-sm focus:border-white outline-none transition" placeholder="E-Posta">
                <input type="password" id="authPass" class="w-full p-4 rounded-xl bg-[#111] border border-[#222] text-sm focus:border-white outline-none transition" placeholder="Şifre">
            </div>
            <button id="btnLogin" class="w-full p-4 bg-white text-black rounded-xl font-bold mb-4 hover:bg-gray-200">Giriş Yap</button>
            <button id="btnGoogle" class="w-full p-4 bg-[#111] border border-[#222] rounded-xl font-bold flex items-center justify-center gap-2 text-sm"><i class="fab fa-google"></i> Google ile Giriş</button>
        </div>
    </div>

    <aside id="sidebar" class="sidebar">
        <div class="p-5 border-b border-[#222] flex justify-between items-center">
            <span class="font-bold tracking-tighter"><i class="fas fa-cube mr-2"></i>LEGENDS PRO</span>
            <button id="closeSidebar" class="md:hidden"><i class="fas fa-times"></i></button>
        </div>
        <div class="p-4"><button id="newChatBtn" class="w-full p-3 border border-[#333] rounded-xl text-sm hover:bg-[#111] transition flex items-center gap-2"><i class="fas fa-plus"></i> Yeni Sohbet</button></div>
        <div id="historyList" class="flex-1 overflow-y-auto px-3 space-y-1 text-xs text-gray-500"></div>
        <div class="p-5 border-t border-[#222] flex items-center justify-between text-xs">
            <div class="flex items-center gap-2 truncate" id="userTag"><div class="w-7 h-7 bg-white text-black rounded-full flex items-center justify-center font-bold">Ş</div> <span id="uName">Patron</span></div>
            <i class="fas fa-cog cursor-pointer hover:text-white" id="openSettings"></i>
        </div>
    </aside>

    <main class="flex-1 flex flex-col relative h-full">
        <header class="h-14 border-b border-[#111] flex items-center px-4 md:hidden"><i class="fas fa-bars mr-4" id="openSidebar"></i> <span class="font-bold text-sm">LEGENDS PRO</span></header>
        <div id="chat-container" class="flex-1 overflow-y-auto p-4 md:p-10 pb-40 space-y-6">
            <div class="h-full flex flex-col items-center justify-center text-gray-700 opacity-20"><i class="fas fa-cube text-6xl mb-6"></i><p class="font-bold">v23.0 ULTIMATE</p></div>
        </div>

        <div class="absolute bottom-0 w-full p-4 md:p-10 bg-gradient-to-t from-black via-black to-transparent">
            <div class="max-w-3xl mx-auto bg-[#080808] border border-[#222] rounded-2xl p-2 flex items-end gap-2 focus-within:border-[#444] transition shadow-2xl">
                <button id="fileBtn" class="p-3 text-gray-500 hover:text-white"><i class="fas fa-paperclip"></i></button>
                <textarea id="userInput" class="flex-1 bg-transparent border-none text-white py-3 text-sm outline-none resize-none max-h-[180px]" placeholder="Emirlerini yaz patron..." rows="1"></textarea>
                <button id="sendBtn" class="p-3 bg-white text-black rounded-xl hover:scale-105 transition mb-0.5"><i class="fas fa-arrow-up"></i></button>
            </div>
        </div>
    </main>

    <div id="settingsModal" class="modal">
        <div class="bg-[#080808] border border-[#222] p-8 rounded-2xl w-full max-w-sm">
            <div class="flex justify-between items-center mb-8 font-bold"><span>AYARLAR</span> <i class="fas fa-times cursor-pointer" id="closeSettings"></i></div>
            <div class="space-y-6">
                <div><label class="flex justify-between text-[10px] text-gray-500 font-bold mb-3 uppercase"><span>Sıcaklık (Temp)</span><span id="tVal">0.2</span></label>
                <input type="range" id="tRange" min="0" max="1" step="0.1" value="0.2" class="w-full accent-white h-1 bg-[#222] rounded-full appearance-none"></div>
                <div class="p-6 bg-[#111] border border-[#222] rounded-xl text-center"><h3 class="font-bold text-xs mb-2">AI EĞİTME</h3><p class="text-[10px] text-gray-500 mb-4">Özel verilerini yükle ve analiz et.</p><button class="w-full p-3 bg-white text-black rounded-lg text-xs font-bold">VERİ YÜKLE</button></div>
                <button id="btnLogout" class="w-full p-3 border border-red-900 text-red-600 rounded-lg text-xs font-bold hover:bg-red-900/10">OTURUMU KAPAT</button>
            </div>
        </div>
    </div>

    <div id="previewModal" class="modal">
        <div class="bg-black border border-[#222] w-[95%] h-[90vh] rounded-2xl overflow-hidden flex flex-col">
            <div class="p-4 border-b border-[#222] flex justify-between items-center bg-[#050505]"><span class="text-[10px] font-bold text-gray-500">CANLI ÖNİZLEME</span><i class="fas fa-times cursor-pointer" id="closePreview"></i></div>
            <iframe id="pFrame" class="flex-1 w-full bg-white"></iframe>
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

        // [object Object] HATASINI ÇÖZEN ÖZEL RENDERER
        const renderer = new marked.Renderer();
        renderer.code = function(code, lang) {
            // Kodun string olduğundan emin oluyoruz
            const cleanCode = typeof code === 'object' ? JSON.stringify(code, null, 2) : String(code);
            const escaped = cleanCode.replace(/`/g, '\\`').replace(/'/g, "\\'");
            return `<div class="relative">
                <div class="code-header">
                    <button onclick="window.uCode(\`${escaped}\`)" class="code-btn btn-v2">Güncelle v2</button>
                    <button onclick="window.cCode(\`${escaped}\`, this)" class="code-btn">Kopyala</button>
                    <button onclick="window.pCode(\`${escaped}\`)" class="code-btn btn-pre">Önizle</button>
                </div>
                <pre><code>${cleanCode}</code></pre>
            </div>`;
        };
        marked.setOptions({ renderer: renderer });

        window.uCode = (c) => { document.getElementById('userInput').value = `Mevcut kodu bozmadan geliştir:\\n\\n\`\`\`\\n${c}\`\`\``; document.getElementById('userInput').focus(); };
        window.cCode = (c, b) => { navigator.clipboard.writeText(c); b.innerText = 'OK'; setTimeout(()=>b.innerText='Kopyala', 2000); };
        window.pCode = (c) => { document.getElementById('previewModal').classList.add('active'); document.getElementById('pFrame').srcdoc = c; };

        onAuthStateChanged(auth, (u) => {
            if(u){
                cUser = u; document.getElementById('auth-screen').style.display = 'none';
                document.getElementById('uName').innerText = u.email.split('@')[0];
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
                    div.className = `p-3 rounded-lg cursor-pointer flex justify-between items-center group transition ${active ? 'bg-[#111] text-white' : 'hover:bg-[#080808]'}`;
                    div.innerHTML = `<span class="truncate pr-2">${d.data().title || 'Yeni Sohbet'}</span><i class="fas fa-trash-alt opacity-0 group-hover:opacity-50 hover:text-red-500" onclick="event.stopPropagation(); window.delC('${d.id}')"></i>`;
                    div.onclick = () => loadC(d.id); l.appendChild(div);
                });
            });
        }

        async function startN() {
            cChatId = "chat_" + Date.now(); history = [];
            document.getElementById('chat-container').innerHTML = '<div class="h-full flex flex-col items-center justify-center text-gray-700 opacity-20"><i class="fas fa-cube text-6xl mb-6"></i><p class="font-bold uppercase tracking-widest">Legends Master v23</p></div>';
            await setDoc(doc(db, `users/${cUser.uid}/chats`, cChatId), { title: "Yeni Sohbet", updatedAt: serverTimestamp(), messages: [] });
        }

        async function loadC(id) {
            cChatId = id; const d = await getDoc(doc(db, `users/${cUser.uid}/chats`, id));
            if(d.exists()){ history = d.data().messages || []; renderC(); }
        }
        window.delC = async (id) => { if(confirm("Silinsin mi?")) { await deleteDoc(doc(db, `users/${cUser.uid}/chats`, id)); startN(); } };

        document.getElementById('sendBtn').onclick = sendM;
        document.getElementById('userInput').oninput = function() { this.style.height = 'auto'; this.style.height = this.scrollHeight + 'px'; };
        document.getElementById('userInput').onkeydown = (e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendM(); } };

        async function sendM() {
            const v = document.getElementById('userInput').value.trim(); if(!v) return;
            if(history.length === 0) document.getElementById('chat-container').innerHTML = '';
            
            document.getElementById('userInput').value = ""; document.getElementById('userInput').style.height = 'auto';
            addUI(v, 'user'); history.push({role: "user", content: v});
            
            const lId = "ai_" + Date.now();
            document.getElementById('chat-container').innerHTML += `<div id="${lId}" class="msg-ai text-gray-500"><div class="w-8 h-8 border border-[#222] rounded-full flex items-center justify-center bg-white"><i class="fas fa-cube text-xs text-black"></i></div><div class="flex items-center gap-1"><div class="typing"></div><div class="typing" style="animation-delay:0.2s"></div><div class="typing" style="animation-delay:0.4s"></div></div></div>`;
            document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;

            try {
                const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ messages: history, settings: config }) });
                const d = await res.json();
                document.getElementById(lId).remove();
                addUI(d.answer, 'assistant'); history.push({role: "assistant", content: d.answer});
                await updateDoc(doc(db, `users/${cUser.uid}/chats`, cChatId), { title: history[0].content.substring(0, 30), messages: history, updatedAt: serverTimestamp() });
            } catch(e) { document.getElementById(lId).innerHTML = "❌ Hata: İnterneti kontrol et patron."; }
        }

        function addUI(t, r) {
            const d = document.createElement('div'); d.className = r === 'user' ? 'msg-user' : 'msg-ai';
            if(r === 'user') d.innerText = t;
            else d.innerHTML = `<div class="w-8 h-8 border border-[#222] rounded-full flex items-center justify-center bg-white flex-shrink-0"><i class="fas fa-cube text-xs text-black"></i></div><div class="flex-1 overflow-hidden">${marked.parse(t)}</div>`;
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
        document.getElementById('fileBtn').onclick = () => alert('Firebase Storage entegrasyonu v24 için planlandı patron!');
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

