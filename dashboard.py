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
DEFAULT_PROMPT = "Sen Legends Master Pro v29'sun. Şenol Kocabıyık'ın (19) baş mimarısın. Her dilde mükemmel kod yaz. v1/v2 mantığıyla çalış. Profesyonel ol."

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
    <meta charset="UTF-8"><title>Legends Pro v29 - Mobile Edition</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css">
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/toastify-js"></script>
    <style>
        /* TEMEL MOBİL AYARLAR */
        body { background: #000; color: #fff; display: flex; height: 100dvh; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; -webkit-tap-highlight-color: transparent; }
        
        /* MOBİL SİDEBAR (GİZLİ BAŞLAR, YANDAN AÇILIR) */
        .sidebar { position: absolute; transform: translateX(-100%); z-index: 50; height: 100%; width: 85%; max-width: 320px; background: #050505; border-right: 1px solid #1a1a1a; display: flex; flex-direction: column; transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 10px 0 30px rgba(0,0,0,0.8); }
        .sidebar.open { transform: translateX(0); }
        
        /* MOBİL MESAJ ALANI */
        #chat-container { flex: 1; overflow-y: auto; padding: 16px; padding-bottom: 90px; -webkit-overflow-scrolling: touch; }
        .msg-user { background: #3b82f6; border-radius: 20px 20px 4px 20px; padding: 12px 16px; margin: 8px 0 16px auto; max-width: 90%; font-size: 14px; box-shadow: 0 4px 12px rgba(59,130,246,0.3); }
        .msg-ai { padding: 12px 0 24px 0; border-bottom: 1px solid #111; display: flex; flex-direction: column; gap: 8px; }
        .ai-header { display: flex; items-center; gap: 8px; font-size: 11px; font-weight: 800; color: #888; text-transform: uppercase; }
        .ai-avatar { width: 24px; height: 24px; border-radius: 6px; background: #fff; color: #000; display: flex; align-items: center; justify-content: center; font-size: 10px; }
        .markdown-body { font-size: 14px; line-height: 1.6; color: #e5e5e5; word-wrap: break-word; }
        
        /* MOBİL İÇİN KUSURSUZ KOD BLOKLARI */
        pre { background: #0a0a0a !important; border: 1px solid #222; border-radius: 12px 12px 0 0; padding: 16px; margin-top: 12px; margin-bottom: 0; overflow-x: auto; -webkit-overflow-scrolling: touch; font-size: 12px; max-width: 100vw; }
        .code-toolbar { background: #111; border: 1px solid #222; border-top: none; border-radius: 0 0 12px 12px; padding: 8px; display: flex; gap: 6px; margin-bottom: 24px; overflow-x: auto; -webkit-overflow-scrolling: touch; }
        
        /* MOBİL DOKUNMATİK BUTONLAR (ESNİYOR VE BÜYÜYOR) */
        .code-btn { flex: 1; padding: 10px 4px; border-radius: 8px; font-size: 11px; font-weight: 800; background: #222; color: #fff; border: 1px solid #333; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 4px; white-space: nowrap; transition: 0.1s; }
        .code-btn:active { transform: scale(0.95); background: #444; }
        .btn-v2 { background: #3b82f6; border-color: #2563eb; } .btn-pre { background: #16a34a; border-color: #15803d; }
        
        /* MOBİL INPUT ALANI (KLAVYE DOSTU) */
        .input-wrapper { position: absolute; bottom: 0; left: 0; right: 0; padding: 12px; padding-bottom: max(12px, env(safe-area-inset-bottom)); background: linear-gradient(to top, rgba(0,0,0,1) 70%, rgba(0,0,0,0)); z-index: 40; }
        .input-box { background: #111; border: 1px solid #333; border-radius: 24px; padding: 4px 6px; display: flex; align-items: flex-end; gap: 6px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }
        textarea { flex: 1; background: transparent; border: none; color: white; padding: 12px 8px; font-size: 15px; outline: none; resize: none; max-height: 120px; }
        .send-btn { background: #3b82f6; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; margin-bottom: 2px; flex-shrink: 0; }
        
        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.95); z-index: 100; align-items: center; justify-content: center; backdrop-filter: blur(10px); padding: 16px; }
        .modal.active { display: flex; }
        .typing::after { content: '|'; animation: blink 1s infinite; color: #3b82f6; }
        @keyframes blink { 50% { opacity: 0; } }

        /* Tablet/Desktop Override */
        @media (min-width: 768px) {
            .sidebar { position: relative; transform: translateX(0); width: 300px; }
            .msg-ai { flex-direction: row; padding: 24px 0; gap: 16px; }
            .ai-header { display: none; }
            .code-btn { flex: none; padding: 8px 16px; }
            .code-toolbar { justify-content: flex-end; }
        }
    </style>
</head>
<body>
    <div id="auth-screen" class="fixed inset-0 z-[1000] bg-black flex items-center justify-center p-6">
        <div class="bg-[#0a0a0a] border border-[#222] p-8 rounded-[32px] w-full max-w-sm text-center shadow-2xl relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-purple-500"></div>
            <i class="fas fa-cube text-5xl mb-6 text-white"></i><h1 class="text-2xl font-black mb-6">LEGENDS PRO</h1>
            <div class="space-y-3 mb-6">
                <input type="email" id="authEmail" class="w-full p-4 rounded-2xl bg-[#111] border border-[#333] text-sm focus:border-blue-500 outline-none" placeholder="E-Posta Adresi">
                <input type="password" id="authPass" class="w-full p-4 rounded-2xl bg-[#111] border border-[#333] text-sm focus:border-blue-500 outline-none" placeholder="Şifre Oluştur/Gir">
            </div>
            <div class="flex gap-2 mb-6">
                <button id="btnLogin" class="flex-1 py-4 bg-blue-600 text-white rounded-2xl font-bold text-sm">Giriş Yap</button>
                <button id="btnRegister" class="flex-1 py-4 bg-[#222] text-white rounded-2xl font-bold border border-[#444] text-sm">Kayıt Ol</button>
            </div>
            <button id="btnGoogle" class="w-full p-4 bg-white text-black rounded-2xl font-bold flex justify-center items-center gap-2 text-sm"><i class="fab fa-google text-lg"></i> Google ile Giriş</button>
        </div>
    </div>

    <aside id="sidebar" class="sidebar">
        <div class="p-5 border-b border-[#222] flex justify-between items-center"><span class="font-black text-lg text-white">LEGENDS PRO</span><i class="fas fa-times text-xl text-gray-500 p-2" id="closeSidebar"></i></div>
        <div class="p-4"><button id="newChatBtn" class="w-full p-4 bg-blue-600/10 border border-blue-600/20 text-blue-500 rounded-2xl font-bold text-sm"><i class="fas fa-plus mr-2"></i> YENİ PROJE</button></div>
        <div id="historyList" class="flex-1 overflow-y-auto px-4 space-y-2"></div>
        <div class="p-5 border-t border-[#222] flex justify-between items-center bg-[#0a0a0a]"><span id="uName" class="font-bold text-sm">Patron</span><i class="fas fa-cog text-xl text-gray-500 p-2" id="openSettings"></i></div>
    </aside>

    <main class="flex-1 flex flex-col relative">
        <header class="p-4 border-b border-[#111] flex items-center bg-[#050505] z-10 shadow-md md:hidden">
            <i class="fas fa-bars text-xl mr-4 text-gray-400 p-1" id="openSidebar"></i>
            <span class="font-black tracking-widest text-sm">LEGENDS PRO</span>
        </header>
        
        <div id="chat-container">
            <div class="h-full flex flex-col items-center justify-center pt-32 opacity-20"><i class="fas fa-cube text-7xl mb-4"></i><p class="font-black tracking-widest text-xs">MOBILE ARCHITECT</p></div>
        </div>
        
        <div class="input-wrapper">
            <div class="input-box max-w-4xl mx-auto">
                <textarea id="userInput" placeholder="Yazılım emrini ver..." rows="1"></textarea>
                <button id="sendBtn" class="send-btn"><i class="fas fa-arrow-up"></i></button>
            </div>
        </div>
    </main>

    <div id="settingsModal" class="modal">
        <div class="bg-[#0a0a0a] border border-[#222] p-6 rounded-[32px] w-full max-w-md relative">
            <div class="flex justify-between font-black mb-6 text-lg"><span>AYARLAR</span><i class="fas fa-times text-gray-500 p-1" id="closeSettings"></i></div>
            <div class="space-y-6">
                <div><label class="text-xs font-bold text-gray-500 mb-2 block uppercase">Yaratıcılık (<span id="tVal">0.2</span>)</label><input type="range" id="tRange" min="0" max="1" step="0.1" value="0.2" class="w-full accent-blue-500 h-2 bg-[#222] rounded-full appearance-none"></div>
                <div class="p-4 bg-[#111] rounded-2xl border border-[#222]"><label class="text-xs font-bold text-blue-500 block mb-2 uppercase"><i class="fas fa-brain"></i> AI Özel Karakteri</label><textarea id="sysPrompt" class="w-full bg-black border border-[#333] rounded-xl p-3 text-xs text-white outline-none resize-none" rows="4" placeholder="Karakter belirle..."></textarea><button id="saveSet" class="w-full mt-3 p-3 bg-[#222] rounded-xl text-xs font-bold hover:bg-[#333]">KAYDET</button></div>
                <button id="btnLogout" class="w-full p-4 border border-red-900/50 text-red-500 rounded-2xl text-xs font-black">OTURUMU KAPAT</button>
            </div>
        </div>
    </div>

    <div id="previewModal" class="modal"><div class="bg-black border border-[#222] w-full h-full md:h-[90vh] md:w-[95%] rounded-[32px] flex flex-col overflow-hidden"><div class="p-4 border-b border-[#222] flex justify-between items-center bg-[#050505]"><span class="text-[10px] font-black text-gray-500 uppercase tracking-widest">ÖNİZLEME MOTORU</span><i class="fas fa-times text-xl text-gray-500 p-2" id="closePreview"></i></div><iframe id="pFrame" class="flex-1 bg-white" sandbox="allow-scripts allow-modals"></iframe></div></div>

    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
        import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut, signInWithEmailAndPassword, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
        import { getFirestore, collection, doc, setDoc, getDoc, updateDoc, deleteDoc, query, orderBy, onSnapshot, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";
        
        const app = initializeApp({ apiKey: "AIzaSyAnNzL2wSLEsy6DprleCNSq9elnv3X7BTg", authDomain: "legendsai-3e2d6.firebaseapp.com", projectId: "legendsai-3e2d6" });
        const auth = getAuth(app); const db = getFirestore(app);
        let cUser = null, cChatId = null, history = [], config = { temperature: 0.2, systemPrompt: "" };
        const toast = (m, type='info') => Toastify({text: m, duration: 3000, style: {background: type==='error'?"#ef4444":"#3b82f6", borderRadius: "12px", fontSize: "12px", fontWeight: "bold"}}).showToast();

        const renderer = new marked.Renderer();
        renderer.code = function(code, lang) {
            const raw = typeof code === 'object' ? code.text : String(code);
            const esc = raw.replace(/`/g, '\\`').replace(/'/g, "\\'").replace(/"/g, '&quot;');
            const isH = (lang === 'html' || raw.toLowerCase().includes('<!doctype') || raw.toLowerCase().includes('<html>'));
            // MOBİL İÇİN KISA İSİMLİ VE İKONLU BUTONLAR
            return `<pre><code class="language-${lang}">${raw}</code></pre><div class="code-toolbar"><button onclick="window.uC(\`${esc}\`)" class="code-btn btn-v2"><i class="fas fa-level-up-alt"></i> v2</button><button onclick="window.cC(\`${esc}\`, this)" class="code-btn"><i class="fas fa-copy"></i> Al</button>${isH ? `<button onclick="window.pC(\`${esc}\`)" class="code-btn btn-pre"><i class="fas fa-play"></i> İzle</button>` : ''}</div>`;
        };
        marked.setOptions({ renderer: renderer });
        window.uC = (c) => { document.getElementById('userInput').value = `Mevcut kodu bozmadan v2 yap:\\n\\n\`\`\`\\n${c}\`\`\``; document.getElementById('userInput').focus(); };
        window.cC = (c, b) => { navigator.clipboard.writeText(c); b.innerHTML = '<i class="fas fa-check"></i>'; setTimeout(()=>b.innerHTML='<i class="fas fa-copy"></i> Al', 2000); toast('Kopyalandı.'); };
        window.pC = (c) => { document.getElementById('previewModal').classList.add('active'); document.getElementById('pFrame').srcdoc = c; };

        document.getElementById('btnLogin').onclick = () => signInWithEmailAndPassword(auth, document.getElementById('authEmail').value, document.getElementById('authPass').value).catch(e => toast("Hata: " + e.message, 'error'));
        document.getElementById('btnRegister').onclick = () => createUserWithEmailAndPassword(auth, document.getElementById('authEmail').value, document.getElementById('authPass').value).then(() => toast('Kayıt başarılı!')).catch(e => toast("Hata: " + e.message, 'error'));
        document.getElementById('btnGoogle').onclick = () => signInWithPopup(auth, new GoogleAuthProvider()).catch(e => toast(e.message, 'error'));
        document.getElementById('btnLogout').onclick = () => { signOut(auth); document.getElementById('settingsModal').classList.remove('active'); };

        onAuthStateChanged(auth, async (u) => {
            if(u){ cUser = u; document.getElementById('auth-screen').style.display = 'none'; document.getElementById('uName').innerText = u.email.split('@')[0].toUpperCase();
                const d = await getDoc(doc(db, `users/${u.uid}/settings`, 'cfg')); if(d.exists()){ config = d.data(); document.getElementById('tRange').value = config.temperature; document.getElementById('sysPrompt').value = config.systemPrompt || ""; }
                onSnapshot(query(collection(db, `users/${u.uid}/chats`), orderBy('updatedAt', 'desc')), (s) => {
                    const l = document.getElementById('historyList'); l.innerHTML = "";
                    s.forEach(d => { const div = document.createElement('div'); div.className = `p-4 mb-2 rounded-2xl text-xs font-bold cursor-pointer flex justify-between items-center ${cChatId===d.id ? 'bg-[#111] border border-[#333] text-white' : 'bg-[#0a0a0a] text-gray-500 border border-[#111]'} transition-all`; div.innerHTML = `<span class="truncate">${d.data().title}</span><i class="fas fa-trash text-gray-700 active:text-red-500 p-2" onclick="event.stopPropagation(); window.dC('${d.id}')"></i>`; div.onclick = () => { loadC(d.id); document.getElementById('sidebar').classList.remove('open'); }; l.appendChild(div); });
                }); startN();
            } else { document.getElementById('auth-screen').style.display = 'flex'; }
        });

        document.getElementById('saveSet').onclick = async () => { config.systemPrompt = document.getElementById('sysPrompt').value; await setDoc(doc(db, `users/${cUser.uid}/settings`, 'cfg'), config); toast('Eğitim Kaydedildi.'); document.getElementById('settingsModal').classList.remove('active'); };

        async function startN() { cChatId = "chat_"+Date.now(); history = []; document.getElementById('chat-container').innerHTML = ''; await setDoc(doc(db, `users/${cUser.uid}/chats`, cChatId), { title: "Yeni Proje", updatedAt: serverTimestamp(), messages: [] }); document.getElementById('sidebar').classList.remove('open'); }
        async function loadC(id) { cChatId = id; const d = await getDoc(doc(db, `users/${cUser.uid}/chats`, id)); if(d.exists()){ history = d.data().messages || []; rC(); } }
        window.dC = async (id) => { await deleteDoc(doc(db, `users/${cUser.uid}/chats`, id)); startN(); toast('Proje Silindi.', 'error'); };

        document.getElementById('sendBtn').onclick = sM;
        document.getElementById('userInput').oninput = function() { this.style.height = 'auto'; this.style.height = (this.scrollHeight) + 'px'; };

async function sM() {
            const v = document.getElementById('userInput').value.trim(); if(!v) return;
            document.getElementById('userInput').value = ""; document.getElementById('userInput').style.height = 'auto'; addUI(v, 'user'); history.push({role: "user", content: v});
            const d = document.createElement('div'); d.className = 'msg-ai'; d.innerHTML = `<div class="ai-header"><div class="ai-avatar"><i class="fas fa-cube"></i></div><span>MİMAR</span></div><div class="markdown-body typing"></div>`;
            document.getElementById('chat-container').appendChild(d); document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
            let full = ""; const cDiv = d.querySelector('.markdown-body');
            try {
                const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ messages: history, settings: config }) });
                const r = res.body.getReader(); const dec = new TextDecoder();
                while (true) { const { done, value } = await r.read(); if (done) break; full += dec.decode(value, {stream: true}); cDiv.innerHTML = marked.parse(full); document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight; }
                cDiv.classList.remove('typing'); history.push({role: "assistant", content: full}); await updateDoc(doc(db, `users/${cUser.uid}/chats`, cChatId), { title: history[0].content.substring(0,25), messages: history, updatedAt: serverTimestamp() });
            } catch(e) { cDiv.innerHTML = "Sinyal koptu patron."; cDiv.classList.remove('typing'); }
        }
        function addUI(t, r) { const d = document.createElement('div'); d.className = r==='user'?'msg-user':'msg-ai'; if(r==='user') d.innerText=t; else d.innerHTML=`<div class="ai-header"><div class="ai-avatar"><i class="fas fa-cube"></i></div><span>MİMAR</span></div><div class="markdown-body">${marked.parse(t)}</div>`; document.getElementById('chat-container').appendChild(d); }
        function rC() { document.getElementById('chat-container').innerHTML = ""; history.forEach(m => addUI(m.content, m.role)); }
        
        document.getElementById('openSidebar').onclick = () => document.getElementById('sidebar').classList.add('open');
        document.getElementById('closeSidebar').onclick = () => document.getElementById('sidebar').classList.remove('open');
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
