from flask import Flask, render_template_string, request, jsonify, Response, stream_with_context
import os, requests, json

app = Flask(__name__)

API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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"
]
MODEL = "llama-3.3-70b-versatile"
DEFAULT_PROMPT = "Sen Legends Master Pro v28.3'sün. Şenol Kocabıyık'ın baş mimarısın. Her dilde mükemmel kod yaz. v1/v2 mantığıyla çalış. Profesyonel ve siberpunk ol."

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    custom_prompt = data.get('settings', {}).get('systemPrompt', DEFAULT_PROMPT)
    if not custom_prompt.strip(): custom_prompt = DEFAULT_PROMPT
    full_messages = [{"role": "system", "content": custom_prompt}] + data.get('messages', [])[-15:]
    temp = float(data.get('settings', {}).get('temperature', 0.2))

    def generate():
        key_idx = 0
        attempts = 0
        while attempts < len(API_KEYS):
            try:
                with requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {API_KEYS[key_idx]}", "Content-Type": "application/json"},
                    json={"model": MODEL, "messages": full_messages, "temperature": temp, "max_tokens": 4096, "stream": True},
                    stream=True, timeout=20
                ) as resp:
                    if resp.status_code == 200:
                        for line in resp.iter_lines():
                            if line:
                                dec = line.decode('utf-8').replace('data: ', '')
                                if dec != '[DONE]':
                                    try:
                                        content = json.loads(dec)['choices'][0]['delta'].get('content')
                                        if content: yield content
                                    except: pass
                        return
                    else: raise Exception("API Error")
            except Exception:
                key_idx = (key_idx + 1) % len(API_KEYS)
                attempts += 1
        yield "❌ Sunucu yoğun patron."
    return Response(stream_with_context(generate()), mimetype='text/plain')

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
    <meta charset="UTF-8"><title>Legends Pro v28.3</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css">
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/toastify-js"></script>
    <style>
        body { background: #000; color: #fff; display: flex; height: 100dvh; overflow: hidden; font-family: sans-serif; }
        .sidebar { width: 280px; background: #050505; border-right: 1px solid #1a1a1a; display: flex; flex-direction: column; transition: 0.3s; }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; }
        .msg-user { background: #3b82f6; border-radius: 16px 16px 4px 16px; padding: 12px 16px; margin: 8px 0 8px auto; max-width: 85%; font-size: 14px; }
        .msg-ai { padding: 20px 0; border-bottom: 1px solid #111; display: flex; gap: 12px; }
        pre { background: #0a0a0a !important; border: 1px solid #222; border-radius: 12px 12px 0 0; padding: 20px; margin-top: 16px; overflow-x: auto; }
        .code-toolbar { background: #111; border: 1px solid #222; border-top: none; border-radius: 0 0 12px 12px; padding: 8px; display: flex; justify-content: flex-end; gap: 6px; margin-bottom: 16px; }
        .code-btn { padding: 6px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; background: #222; color: #fff; border: 1px solid #333; cursor: pointer; }
        .code-btn:hover { background: #333; } .btn-v2 { background: #3b82f6; border-color: #3b82f6; } .btn-pre { background: #16a34a; border-color: #15803d; }
        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.9); z-index: 50; align-items: center; justify-content: center; backdrop-filter: blur(10px); }
        .modal.active { display: flex; }
        .typing::after { content: '|'; animation: blink 1s infinite; color: #3b82f6; }
        @keyframes blink { 50% { opacity: 0; } }
        @media (max-width: 768px) { .sidebar { position: absolute; transform: translateX(-100%); z-index: 40; height: 100%; } .sidebar.open { transform: translateX(0); } }
    </style>
</head>
<body>
    <div id="auth-screen" class="fixed inset-0 z-50 bg-black flex items-center justify-center p-6">
        <div class="bg-[#0a0a0a] border border-[#222] p-10 rounded-3xl w-full max-w-sm text-center shadow-2xl relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-purple-500"></div>
            <i class="fas fa-cube text-5xl mb-6 text-white"></i><h1 class="text-2xl font-black mb-8">LEGENDS PRO</h1>
            
            <div class="space-y-4 mb-6">
                <input type="email" id="authEmail" class="w-full p-4 rounded-xl bg-[#111] border border-[#333] text-sm focus:border-blue-500 outline-none transition" placeholder="E-Posta Adresi">
                <input type="password" id="authPass" class="w-full p-4 rounded-xl bg-[#111] border border-[#333] text-sm focus:border-blue-500 outline-none transition" placeholder="Şifre Oluştur / Gir">
            </div>
            
            <div class="flex gap-3 mb-6">
                <button id="btnLogin" class="flex-1 p-4 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition shadow-lg shadow-blue-600/20 text-sm">Giriş Yap</button>
                <button id="btnRegister" class="flex-1 p-4 bg-[#222] text-white rounded-xl font-bold hover:bg-[#333] transition border border-[#444] text-sm">Kayıt Ol</button>
            </div>
            
            <div class="flex items-center gap-4 opacity-30 mb-6"><hr class="flex-1"><span>VEYA</span><hr class="flex-1"></div>
            
            <button id="btnGoogle" class="w-full p-4 bg-white text-black rounded-xl font-bold flex justify-center items-center gap-2 hover:bg-gray-200 transition text-sm"><img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" class="w-4 h-4"> Gmail ile Giriş Yap</button>
        </div>
    </div>

    <aside id="sidebar" class="sidebar">
        <div class="p-5 border-b border-[#222] flex justify-between"><span class="font-bold">LEGENDS</span><i class="fas fa-times md:hidden" id="closeSidebar"></i></div>
        <div class="p-4"><button id="newChatBtn" class="w-full p-3 bg-[#111] border border-[#333] rounded-xl font-bold text-sm text-blue-500 hover:bg-[#222]"><i class="fas fa-plus"></i> YENİ PROJE</button></div>
        <div id="historyList" class="flex-1 overflow-y-auto px-4 space-y-2"></div>
        <div class="p-5 border-t border-[#222] flex justify-between items-center"><span id="uName" class="font-bold text-sm">Patron</span><i class="fas fa-cog cursor-pointer" id="openSettings"></i></div>
    </aside>

    <main class="flex-1 flex flex-col relative">
        <header class="p-4 border-b border-[#222] md:hidden flex items-center"><i class="fas fa-bars mr-4" id="openSidebar"></i><span class="font-bold">LEGENDS</span></header>
        <div id="chat-container"><div class="h-full flex flex-col items-center justify-center pt-32 opacity-20"><i class="fas fa-cube text-7xl mb-4"></i><p class="font-black tracking-widest">V28.3 ARCHITECT</p></div></div>
        <div class="p-4 bg-gradient-to-t from-black to-transparent">
            <div class="max-w-4xl mx-auto bg-[#111] border border-[#333] rounded-2xl p-2 flex items-end gap-2">
                <textarea id="userInput" class="flex-1 bg-transparent border-none text-white py-3 px-2 text-sm outline-none resize-none max-h-[150px]" placeholder="Emir ver..." rows="1"></textarea>
                <button id="sendBtn" class="p-3 bg-blue-600 rounded-xl font-bold"><i class="fas fa-arrow-up"></i></button>
            </div>
        </div>
    </main>

    <div id="settingsModal" class="modal">
        <div class="bg-[#0a0a0a] border border-[#222] p-8 rounded-3xl w-full max-w-md">
            <div class="flex justify-between font-bold mb-6"><span>AYARLAR</span><i class="fas fa-times cursor-pointer" id="closeSettings"></i></div>
            <div class="space-y-6">
                <div><label class="text-xs font-bold text-gray-500 mb-2 block">Yaratıcılık (<span id="tVal">0.2</span>)</label><input type="range" id="tRange" min="0" max="1" step="0.1" value="0.2" class="w-full accent-blue-500 h-1 bg-[#222] rounded-full appearance-none"></div>
                <div class="p-4 bg-[#111] rounded-xl border border-[#222]"><label class="text-xs font-bold text-blue-500 block mb-2"><i class="fas fa-brain"></i> AI Eğitimi (Prompt)</label><textarea id="sysPrompt" class="w-full bg-black border border-[#333] rounded-lg p-2 text-xs text-white outline-none" rows="4" placeholder="Karakter belirle..."></textarea><button id="saveSet" class="w-full mt-2 p-2 bg-[#222] rounded-lg text-xs font-bold hover:bg-[#333]">Kaydet</button></div>
                <button id="btnLogout" class="w-full p-3 border border-red-900 text-red-500 rounded-xl text-xs font-bold hover:bg-red-950/40">ÇIKIŞ YAP</button>
            </div>
        </div>
    </div>

    <div id="previewModal" class="modal"><div class="bg-black border border-[#222] w-[95%] h-[90vh] rounded-2xl flex flex-col"><div class="p-4 border-b border-[#222] flex justify-between"><span class="text-xs font-bold text-gray-500">ÖNİZLEME</span><i class="fas fa-times cursor-pointer" id="closePreview"></i></div><iframe id="pFrame" class="flex-1 bg-white" sandbox="allow-scripts allow-modals"></iframe></div></div>

    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
        // createUserWithEmailAndPassword EKLENDİ!
        import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut, signInWithEmailAndPassword, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
        import { getFirestore, collection, doc, setDoc, getDoc, updateDoc, deleteDoc, query, orderBy, onSnapshot, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";
        
        const app = initializeApp({ apiKey: "AIzaSyAnNzL2wSLEsy6DprleCNSq9elnv3X7BTg", authDomain: "legendsai-3e2d6.firebaseapp.com", projectId: "legendsai-3e2d6" });
        const auth = getAuth(app); const db = getFirestore(app);
        let cUser = null, cChatId = null, history = [], config = { temperature: 0.2, systemPrompt: "" };
        const toast = (m, type='info') => Toastify({text: m, duration: 3000, style: {background: type==='error'?"#ef4444":"#3b82f6", borderRadius: "8px", fontSize: "12px", fontWeight: "bold"}}).showToast();

        const renderer = new marked.Renderer();
        renderer.code = function(code, lang) {
            const raw = typeof code === 'object' ? code.text : String(code);
            const esc = raw.replace(/`/g, '\\`').replace(/'/g, "\\'").replace(/"/g, '&quot;');
            const isH = (lang === 'html' || raw.toLowerCase().includes('<!doctype') || raw.toLowerCase().includes('<html>'));
            return `<pre><code class="language-${lang}">${raw}</code></pre><div class="code-toolbar"><button onclick="window.uC(\`${esc}\`)" class="code-btn btn-v2">GÜNCELLE v2</button><button onclick="window.cC(\`${esc}\`, this)" class="code-btn">KOPYALA</button>${isH ? `<button onclick="window.pC(\`${esc}\`)" class="code-btn btn-pre">ÖNİZLE</button>` : ''}</div>`;
        };
        marked.setOptions({ renderer: renderer });
        window.uC = (c) => { document.getElementById('userInput').value = `Bu kodu bozmadan v2 yap:\\n\\n\`\`\`\\n${c}\`\`\``; document.getElementById('userInput').focus(); };
        window.cC = (c, b) => { navigator.clipboard.writeText(c); b.innerText = 'OK'; setTimeout(()=>b.innerText='KOPYALA', 2000); toast('Kopyalandı.'); };
        window.pC = (c) => { document.getElementById('previewModal').classList.add('active'); document.getElementById('pFrame').srcdoc = c; };

        // FIREBASE GİRİŞ VE KAYIT SİSTEMİ BÖLÜMÜ
        document.getElementById('btnLogin').onclick = () => {
            signInWithEmailAndPassword(auth, document.getElementById('authEmail').value, document.getElementById('authPass').value).catch(e => toast("Hata: " + e.message, 'error'));
        };
        document.getElementById('btnRegister').onclick = () => {
            createUserWithEmailAndPassword(auth, document.getElementById('authEmail').value, document.getElementById('authPass').value)
                .then(() => toast('Kayıt başarılı! Hoş geldin.'))
                .catch(e => toast("Hata: " + e.message, 'error'));
        };
        document.getElementById('btnGoogle').onclick = () => signInWithPopup(auth, new GoogleAuthProvider()).catch(e => toast(e.message, 'error'));
        document.getElementById('btnLogout').onclick = () => { signOut(auth); document.getElementById('settingsModal').classList.remove('active'); };

        onAuthStateChanged(auth, async (u) => {
            if(u){ cUser = u; document.getElementById('auth-screen').style.display = 'none'; document.getElementById('uName').innerText = u.email.split('@')[0];
                const d = await getDoc(doc(db, `users/${u.uid}/settings`, 'cfg')); if(d.exists()){ config = d.data(); document.getElementById('tRange').value = config.temperature; document.getElementById('sysPrompt').value = config.systemPrompt || ""; }
                onSnapshot(query(collection(db, `users/${u.uid}/chats`), orderBy('updatedAt', 'desc')), (s) => {
                    const l = document.getElementById('historyList'); l.innerHTML = "";
                    s.forEach(d => { const div = document.createElement('div'); div.className = `p-3 mb-1 rounded-xl text-xs font-bold cursor-pointer flex justify-between group ${cChatId===d.id ? 'bg-[#222] text-white' : 'text-gray-500 hover:bg-[#111]'}`; div.innerHTML = `<span class="truncate">${d.data().title}</span><i class="fas fa-trash opacity-0 group-hover:opacity-100 text-red-500" onclick="event.stopPropagation(); window.dC('${d.id}')"></i>`; div.onclick = () => loadC(d.id); l.appendChild(div); });
                }); startN();
            } else { document.getElementById('auth-screen').style.display = 'flex'; }
        });

        document.getElementById('saveSet').onclick = async () => { config.systemPrompt = document.getElementById('sysPrompt').value; await setDoc(doc(db, `users/${cUser.uid}/settings`, 'cfg'), config); toast('Kaydedildi.'); };

        async function startN() { cChatId = "chat_"+Date.now(); history = []; document.getElementById('chat-container').innerHTML = ''; await setDoc(doc(db, `users/${cUser.uid}/chats`, cChatId), { title: "Yeni Proje", updatedAt: serverTimestamp(), messages: [] }); }
        async function loadC(id) { cChatId = id; const d = await getDoc(doc(db, `users/${cUser.uid}/chats`, id)); if(d.exists()){ history = d.data().messages || []; rC(); } }
        window.dC = async (id) => { await deleteDoc(doc(db, `users/${cUser.uid}/chats`, id)); startN(); toast('Silindi.'); };

        document.getElementById('sendBtn').onclick = sM;
        document.getElementById('userInput').onkeydown = (e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sM(); } };

        async function sM() {
            const v = document.getElementById('userInput').value.trim(); if(!v) return;
            document.getElementById('userInput').value = ""; addUI(v, 'user'); history.push({role: "user", content: v});
            const d = document.createElement('div'); d.className = 'msg-ai'; d.innerHTML = `<div class="w-8 h-8 rounded-lg bg-white text-black font-bold flex items-center justify-center text-xs">AI</div><div class="flex-1 markdown-body typing"></div>`;
            document.getElementById('chat-container').appendChild(d); document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
            let full = ""; const cDiv = d.querySelector('.markdown-body');
            try {
                const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ messages: history, settings: config }) });
                const r = res.body.getReader(); const dec = new TextDecoder();
                while (true) { const { done, value } = await r.read(); if (done) break; full += dec.decode(value, {stream: true}); cDiv.innerHTML = marked.parse(full); document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight; }
                cDiv.classList.remove('typing'); history.push({role: "assistant", content: full}); await updateDoc(doc(db, `users/${cUser.uid}/chats`, cChatId), { title: history[0].content.substring(0,20), messages: history, updatedAt: serverTimestamp() });
            } catch(e) { cDiv.innerHTML = "Hata oluştu."; cDiv.classList.remove('typing'); }
        }
        function addUI(t, r) { const d = document.createElement('div'); d.className = r==='user'?'msg-user':'msg-ai'; if(r==='user') d.innerText=t; else d.innerHTML=`<div class="w-8 h-8 rounded-lg bg-white text-black font-bold flex items-center justify-center text-xs">AI</div><div class="flex-1 markdown-body">${marked.parse(t)}</div>`; document.getElementById('chat-container').appendChild(d); }
        function rC() { document.getElementById('chat-container').innerHTML = ""; history.forEach(m => addUI(m.content, m.role)); }
        
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

