from flask import Flask, render_template_string, request, jsonify, Response, stream_with_context
import os
import requests
import json

app = Flask(__name__)

# --- 7️⃣ TEKNİK MİMARİ: 10 ANAHTARLI CANLI AKIŞ MOTORU ---
API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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"
]
current_key_index = 0
MODEL = "llama-3.3-70b-versatile"

# VARSAYILAN ANA KİMLİK (Eğer kullanıcı özel bir şey girmezse bu çalışır)
DEFAULT_SYSTEM_PROMPT = """Sen Legends Master Pro v28'sin. Şenol Kocabıyık'ın (19) baş mimarısın.
Görevlerin:
1. Mükemmel, hatasız ve production-ready kod yaz.
2. Kodu yazarken yorum satırlarıyla detaylıca öğret.
3. v1/v2 mantığıyla çalış. 'Güncelle' denildiğinde eski kodu bozmadan üzerine ekleme yap.
4. Cevapların profesyonel ve çözüm odaklı olsun."""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    global current_key_index
    data = request.json
    recent_messages = data.get('messages', [])[-15:]
    settings = data.get('settings', {})
    temp = settings.get('temperature', 0.2)
    
    # --- YENİ: KULLANICI TANIMLI EĞİTİM PROMPTU ---
    # Eğer ayarlardan özel bir prompt geldiyse onu kullan, yoksa varsayılanı kullan.
    custom_prompt = settings.get('systemPrompt', '').strip()
    final_system_prompt = custom_prompt if custom_prompt else DEFAULT_SYSTEM_PROMPT

    full_messages = [{"role": "system", "content": final_system_prompt}] + recent_messages

    def generate():
        global current_key_index
        attempts = 0
        while attempts < len(API_KEYS):
            try:
                with requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {API_KEYS[current_key_index]}", "Content-Type": "application/json"},
                    json={"model": MODEL, "messages": full_messages, "temperature": temp, "max_tokens": 4096, "stream": True},
                    stream=True,
                    timeout=30
                ) as resp:
                    if resp.status_code == 200:
                        for line in resp.iter_lines():
                            if line:
                                decoded_line = line.decode('utf-8').replace('data: ', '')
                                if decoded_line != '[DONE]':
                                    try:
                                        chunk = json.loads(decoded_line)
                                        content = chunk['choices'][0]['delta'].get('content')
                                        if content: yield content
                                    except: pass
                        return
                    else: raise Exception(f"API Hata: {resp.status_code}")
            except Exception as e:
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                attempts += 1
                print(f"Anahtar değişiyor... Hata: {e}")
        yield "❌ Sunucu yoğun patron, anahtarların hepsi denendi."

    return Response(stream_with_context(generate()), mimetype='text/plain')

# --- MÜKEMMEL ARAYÜZ + YENİ EĞİTİM ALANI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
    <meta charset="UTF-8">
    <title>Legends Master Pro | v28.0 Mastermind</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css">
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/toastify-js"></script>
    <style>
        :root { --bg: #000; --panel: #0a0a0a; --border: #1a1a1a; --primary: #fff; --accent: #3b82f6; }
        body { background: var(--bg); color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; height: 100dvh; display: flex; overflow: hidden; }
        .sidebar { width: 300px; background: #030303; border-right: 1px solid var(--border); transition: 0.3s; display: flex; flex-direction: column; }
        .sidebar-item { padding: 14px; border-radius: 12px; cursor: pointer; transition: 0.2s; font-size: 13px; color: #888; border: 1px solid transparent; margin-bottom: 4px; font-weight: 500; }
        .sidebar-item:hover { background: #111; color: #fff; border-color: #222; }
        .sidebar-item.active { background: #111; color: #fff; border-color: var(--accent); }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; scroll-behavior: smooth; }
        .msg-user { background: var(--accent); color: white; border-radius: 20px 20px 4px 20px; padding: 12px 18px; margin: 8px 0 8px auto; max-width: 85%; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2); font-size: 14px; }
        .msg-ai { padding: 24px 0; border-bottom: 1px solid #0f0f0f; display: flex; gap: 16px; animation: fadeIn 0.3s ease; }
        .avatar { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 900; flex-shrink: 0; font-size: 12px; }
        .ai-content { flex: 1; overflow-hidden; font-size: 15px; line-height: 1.7; color: #e5e5e5; }
        
        /* --- KOD BLOKLARI VE BUTONLAR (İSTEDİĞİN GİBİ) --- */
        pre { background: #080808 !important; border: 1px solid var(--border); border-radius: 12px; padding: 50px 16px 16px 16px; margin: 20px 0; position: relative; overflow-x: auto; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); }
        .code-header { position: absolute; top: 12px; right: 12px; display: flex; gap: 8px; opacity: 0; transition: 0.3s; z-index: 10; }
        pre:hover .code-header { opacity: 1; }
        .code-btn { padding: 6px 12px; border-radius: 8px; font-size: 11px; font-weight: 800; cursor: pointer; border: 1px solid #333; color: #fff; transition: 0.2s; background: rgba(0,0,0,0.5); backdrop-filter: blur(5px); display: flex; align-items: center; gap: 6px; }
        .code-btn:hover { background: var(--accent); border-color: var(--accent); }
        .btn-v2 { background: var(--accent); border-color: var(--accent); } /* Güncelle Butonu Rengi */
        .btn-pre { background: #16a34a; border-color: #15803d; } /* Önizle Butonu Rengi */
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .typing-cursor::after { content: '|'; animation: blink 1s infinite; color: var(--accent); }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        .modal { display: none; position: fixed; inset: 0; z-index: 9999; background: rgba(0,0,0,0.95); align-items: center; justify-content: center; backdrop-filter: blur(20px); }
        .modal.active { display: flex; }
        @media (max-width: 768px) { .sidebar { position: absolute; transform: translateX(-100%); z-index: 5000; height: 100%; box-shadow: 10px 0 30px rgba(0,0,0,0.5); } .sidebar.open { transform: translateX(0); } }
    </style>
</head>
<body>
    <div id="auth-screen" class="fixed inset-0 z-[10000] bg-black flex items-center justify-center p-6">
        <div class="border border-[#1a1a1a] bg-[#0a0a0a] p-12 rounded-[40px] w-full max-w-sm text-center shadow-2xl relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"></div>
            <i class="fas fa-cube text-6xl mb-8 text-white"></i><h1 class="text-3xl font-black mb-2 tracking-tighter">LEGENDS PRO</h1><p class="text-gray-500 text-sm mb-10">Mükemmeliyetin Mimarisi</p>
            <div class="space-y-4 mb-8"><input type="email" id="authEmail" class="w-full p-4 rounded-2xl bg-[#111] border border-[#222] text-sm focus:border-blue-500 outline-none transition" placeholder="E-Posta"><input type="password" id="authPass" class="w-full p-4 rounded-2xl bg-[#111] border border-[#222] text-sm focus:border-blue-500 outline-none transition" placeholder="Şifre"></div>
            <button id="btnLogin" class="w-full p-4 bg-blue-600 text-white rounded-2xl font-bold mb-4 hover:scale-[1.02] transition shadow-lg shadow-blue-600/20">Giriş Yap</button>
            <button id="btnGoogle" class="w-full p-4 bg-[#111] border border-[#222] rounded-2xl font-bold flex items-center justify-center gap-2 text-xs transition hover:bg-[#151515]"><i class="fab fa-google"></i> Google ile Devam Et</button>
        </div>
    </div>
    <aside id="sidebar" class="sidebar">
        <div class="p-6 border-b border-[#1a1a1a] flex justify-between items-center"><span class="font-black text-lg tracking-tighter flex items-center gap-2"><i class="fas fa-cube text-blue-500"></i> LEGENDS</span><i class="fas fa-times md:hidden text-gray-500" id="closeSidebar"></i></div>
        <div class="p-4"><button id="newChatBtn" class="w-full p-4 bg-blue-600/10 border border-blue-600/20 text-blue-500 rounded-2xl text-xs font-bold hover:bg-blue-600 hover:text-white transition flex items-center justify-center gap-2"><i class="fas fa-plus"></i> YENİ PROJE BAŞLAT</button></div>
        <div id="historyList" class="flex-1 overflow-y-auto px-4 space-y-2 py-2"></div>
        <div class="p-6 border-t border-[#1a1a1a]"><div class="flex items-center justify-between p-3 bg-[#111] rounded-2xl border border-[#222]"><div class="flex items-center gap-3"><div class="avatar bg-white text-black">ŞK</div><span class="font-bold text-sm" id="uName">Patron</span></div><i class="fas fa-cog text-gray-500 cursor-pointer hover:text-white transition" id="openSettings"></i></div></div>
    </aside>
    <main class="flex-1 flex flex-col relative h-full">
        <header class="h-16 border-b border-[#0a0a0a] flex items-center px-6 md:hidden bg-[#030303]"><i class="fas fa-bars mr-4 text-xl" id="openSidebar"></i><span class="font-bold">LEGENDS PRO</span></header>
        <div id="chat-container"><div class="h-full flex flex-col items-center justify-center text-white opacity-10 select-none pt-40"><i class="fas fa-cube text-8xl mb-6"></i><p class="font-black tracking-[0.5em] text-sm uppercase">V28.0 MASTERMIND</p></div></div>
        <div class="p-6 md:p-12 bg-gradient-to-t from-black via-black to-transparent"><div class="max-w-4xl mx-auto bg-[#0a0a0a] border border-[#1a1a1a] rounded-[32px] p-3 flex items-end gap-3 focus-within:border-blue-500 transition-all shadow-2xl relative z-20"><button class="p-4 text-gray-500 hover:text-white transition" onclick="toast('Dosya sistemi v29 için hazırlanıyor!', 'info')"><i class="fas fa-paperclip text-lg"></i></button><textarea id="userInput" class="flex-1 bg-transparent border-none text-white py-4 text-sm outline-none resize-none max-h-[200px]" placeholder="Mükemmel bir yazılım emri ver..." rows="1"></textarea><button id="sendBtn" class="p-4 bg-blue-600 text-white rounded-[24px] font-black hover:scale-105 active:scale-95 transition-all shadow-lg shadow-blue-600/20"><i class="fas fa-arrow-up"></i></button></div></div>
    </main>

    <div id="settingsModal" class="modal">
        <div class="bg-[#0a0a0a] border border-[#1a1a1a] p-8 rounded-[40px] w-full max-w-md shadow-2xl relative">
            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-purple-500"></div>
            <div class="flex justify-between items-center mb-8 font-black"><span>SİSTEM KONTROLÜ</span><i class="fas fa-times cursor-pointer text-gray-500 hover:text-white" id="closeSettings"></i></div>
            <div class="space-y-6">
                <div><label class="flex justify-between text-[10px] text-gray-500 font-black mb-4 uppercase tracking-widest"><span>Yaratıcılık</span><span id="tVal" class="text-blue-500">0.2</span></label><input type="range" id="tRange" min="0" max="1" step="0.1" value="0.2" class="w-full accent-blue-500 h-2 bg-[#1a1a1a] appearance-none rounded-full"></div>
                
                <div class="p-6 bg-[#030303] border border-[#1a1a1a] rounded-3xl">
                    <h3 class="font-black text-xs mb-3 text-blue-500 flex items-center gap-2"><i class="fas fa-brain"></i> AI KİMLİK EĞİTİMİ</h3>
                    <textarea id="sysPromptInput" rows="4" class="w-full bg-[#111] border border-[#222] rounded-xl p-3 text-xs text-white focus:border-blue-500 outline-none resize-none mb-3 placeholder-gray-600" placeholder="Örn: Sen 20 yıllık bir siber güvenlik uzmanısın. Kodları ona göre analiz et."></textarea>
                    <button id="savePromptBtn" class="w-full p-3 bg-blue-600/20 text-blue-500 rounded-xl text-xs font-bold hover:bg-blue-600 hover:text-white transition flex items-center justify-center gap-2"><i class="fas fa-save"></i> KİMLİĞİ KAYDET</button>
                </div>

                <button id="btnLogout" class="w-full p-4 border border-red-900/50 text-red-500 rounded-2xl text-xs font-black hover:bg-red-950/30 transition">OTURUMU KAPAT</button>
            </div>
        </div>
    </div>

    <div id="previewModal" class="modal"><div class="bg-black border border-[#1a1a1a] w-[98%] h-[95vh] rounded-[32px] overflow-hidden flex flex-col shadow-2xl"><div class="p-5 flex justify-between items-center bg-[#0a0a0a] border-b border-[#1a1a1a]"><div class="flex items-center gap-3"><div class="flex gap-1.5"><div class="w-3 h-3 rounded-full bg-red-500/50"></div><div class="w-3 h-3 rounded-full bg-yellow-500/50"></div><div class="w-3 h-3 rounded-full bg-green-500/50"></div></div><span class="text-[10px] font-black text-gray-500 tracking-[0.2em] uppercase ml-4">Canlı Önizleme</span></div><i class="fas fa-times cursor-pointer text-gray-500 hover:text-white" id="closePreview"></i></div><iframe id="pFrame" class="flex-1 w-full bg-white" sandbox="allow-scripts allow-forms allow-modals"></iframe></div></div>

    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
        import { getAuth, signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut, setPersistence, browserLocalPersistence } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
        import { getFirestore, collection, doc, setDoc, getDoc, updateDoc, deleteDoc, query, orderBy, onSnapshot, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

        const fConfig = { apiKey: "AIzaSyAnNzL2wSLEsy6DprleCNSq9elnv3X7BTg", authDomain: "legendsai-3e2d6.firebaseapp.com", projectId: "legendsai-3e2d6", storageBucket: "legendsai-3e2d6.firebasestorage.app", messagingSenderId: "504400540515", appId: "1:504400540515:web:16cdc9ff57dd8fa2981956" };
        const app = initializeApp(fConfig); const auth = getAuth(app); const db = getFirestore(app);
        setPersistence(auth, browserLocalPersistence);

        // AYARLARI TARAYICIDA SAKLAMA (Kalıcı olması için)
        let config = {
            temperature: parseFloat(localStorage.getItem('temp') || 0.2),
            systemPrompt: localStorage.getItem('savedSystemPrompt') || ''
        };

        // Başlangıçta ayarları yükle
        document.getElementById('tRange').value = config.temperature;
        document.getElementById('tVal').innerText = config.temperature;
        document.getElementById('sysPromptInput').value = config.systemPrompt;

        window.toast = (msg, type='info') => { Toastify({ text: msg, duration: 3000, gravity: "top", position: "center", stopOnFocus: true, style: { background: type === 'error' ? "#ef4444" : "#3b82f6", borderRadius: "12px", boxShadow: "0 10px 30px rgba(0,0,0,0.3)", fontWeight: "bold", fontSize: "13px" } }).showToast(); };

        // --- BUTONLARIN RENDER EDİLDİĞİ YER (İstediğin gibi ayarlandı) ---
        const renderer = new marked.Renderer();
        renderer.code = function(code, lang) {
            const rawCode = typeof code === 'object' ? code.text : String(code);
            const escaped = rawCode.replace(/`/g, '\\`').replace(/'/g, "\\'").replace(/"/g, '&quot;');
            const isHTML = (lang === 'html' || rawCode.toLowerCase().includes('<!doctype') || rawCode.toLowerCase().includes('<html>'));
            // GÜNCELLEME (v2), KOPYALAMA ve ÖNİZLEME Butonları
            return `<div class="relative group">
                <div class="code-header">
                    <button onclick="window.uCode(\`${escaped}\`)" class="code-btn btn-v2"><i class="fas fa-sync-alt"></i> GÜNCELLE v2</button>
                    <button onclick="window.cCode(\`${escaped}\`, this)" class="code-btn"><i class="fas fa-copy"></i> KOPYALA</button>
                    ${isHTML ? `<button onclick="window.pCode(\`${escaped}\`)" class="code-btn btn-pre"><i class="fas fa-play"></i> ÖNİZLE</button>` : ''}
                </div>
                <pre><code class="language-${lang}">${rawCode}</code></pre>
            </div>`;
        };
        marked.setOptions({ renderer: renderer });

// GÜNCELLEME MANTIĞI (Eskiyi silmeden üzerine yazma emri)
        window.uCode = (c) => { document.getElementById('userInput').value = `Bu kodun v1 halini bozmadan, üzerine şu özellikleri ekleyerek v2 sürümünü yap:\\n\\n\`\`\`\\n${c}\`\`\``; document.getElementById('userInput').focus(); };
        window.cCode = (c, b) => { navigator.clipboard.writeText(c); const og = b.innerHTML; b.innerHTML = '<i class="fas fa-check"></i> BİTTİ'; setTimeout(()=>b.innerHTML=og, 2000); toast('Kod panoya kopyalandı.'); };
        window.pCode = (c) => { document.getElementById('previewModal').classList.add('active'); document.getElementById('pFrame').srcdoc = c; };

        let cUser = null, cChatId = null, history = [];
        onAuthStateChanged(auth, (u) => { if(u){ cUser = u; document.getElementById('auth-screen').style.display = 'none'; document.getElementById('uName').innerText = u.email.split('@')[0].toUpperCase(); syncH(); startN(); toast(`Hoş geldin ${u.email.split('@')[0]}!`); } else { document.getElementById('auth-screen').style.display = 'flex'; } });
        document.getElementById('btnLogin').onclick = () => signInWithEmailAndPassword(auth, document.getElementById('authEmail').value, document.getElementById('authPass').value).catch(e => toast(e.message, 'error'));
        document.getElementById('btnGoogle').onclick = () => signInWithPopup(auth, new GoogleAuthProvider()).catch(e => toast(e.message, 'error'));
        document.getElementById('btnLogout').onclick = () => { signOut(auth); document.getElementById('settingsModal').classList.remove('active'); };
        function syncH() { const q = query(collection(db, `users/${cUser.uid}/chats`), orderBy('updatedAt', 'desc')); onSnapshot(q, (s) => { const l = document.getElementById('historyList'); l.innerHTML = ""; s.forEach(d => { const active = cChatId === d.id; const div = document.createElement('div'); div.className = `sidebar-item flex justify-between items-center group ${active ? 'active' : ''}`; div.innerHTML = `<span class="truncate pr-2 font-bold tracking-tight">${d.data().title || 'Yeni Proje'}</span><i class="fas fa-trash-alt opacity-0 group-hover:opacity-40 hover:text-red-500 transition" onclick="event.stopPropagation(); window.delC('${d.id}')"></i>`; div.onclick = () => loadC(d.id); l.appendChild(div); }); }); }
        async function startN() { cChatId = "chat_" + Date.now(); history = []; document.getElementById('chat-container').innerHTML = '<div class="h-full flex flex-col items-center justify-center text-white opacity-10 select-none pt-40"><i class="fas fa-cube text-8xl mb-6"></i><p class="font-black tracking-[0.5em] text-sm uppercase">V28.0 MASTERMIND</p></div>'; await setDoc(doc(db, `users/${cUser.uid}/chats`, cChatId), { title: "Yeni Proje", updatedAt: serverTimestamp(), messages: [] }); }
        async function loadC(id) { cChatId = id; const d = await getDoc(doc(db, `users/${cUser.uid}/chats`, id)); if(d.exists()){ history = d.data().messages || []; renderC(); toast('Proje yüklendi.'); } }
        window.delC = async (id) => { if(confirm("Silinsin mi?")) { await deleteDoc(doc(db, `users/${cUser.uid}/chats`, id)); startN(); toast('Proje silindi.', 'error'); } };
        document.getElementById('sendBtn').onclick = sendM; document.getElementById('userInput').oninput = function() { this.style.height = 'auto'; this.style.height = this.scrollHeight + 'px'; }; document.getElementById('userInput').onkeydown = (e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendM(); } };

        async function sendM() {
            const v = document.getElementById('userInput').value.trim(); if(!v) return;
            if(history.length === 0) document.getElementById('chat-container').innerHTML = '';
            document.getElementById('userInput').value = ""; document.getElementById('userInput').style.height = 'auto';
            addUI(v, 'user'); history.push({role: "user", content: v});
            const aiDiv = document.createElement('div'); aiDiv.className = 'msg-ai';
            aiDiv.innerHTML = `<div class="avatar bg-white text-black shadow-lg shadow-white/10">ŞK</div><div class="ai-content markdown-body typing-cursor"></div>`;
            document.getElementById('chat-container').appendChild(aiDiv); document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
            const contentDiv = aiDiv.querySelector('.ai-content'); let fullResponse = "";
            try {
                const response = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ messages: history, settings: config }) });
                const reader = response.body.getReader(); const decoder = new TextDecoder();
                while (true) { const { done, value } = await reader.read(); if (done) break; fullResponse += decoder.decode(value, {stream: true}); contentDiv.innerHTML = marked.parse(fullResponse); document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight; }
                contentDiv.classList.remove('typing-cursor'); history.push({role: "assistant", content: fullResponse});
                await updateDoc(doc(db, `users/${cUser.uid}/chats`, cChatId), { title: history[0].content.substring(0, 30), messages: history, updatedAt: serverTimestamp() });
            } catch(e) { aiDiv.remove(); toast("Bağlantı hatası.", 'error'); }
        }
        function addUI(t, r) { const d = document.createElement('div'); d.className = r === 'user' ? 'msg-user' : 'msg-ai'; if(r === 'user') d.innerText = t; else d.innerHTML = `<div class="avatar bg-white text-black shadow-lg shadow-white/10">ŞK</div><div class="ai-content markdown-body">${marked.parse(t)}</div>`; document.getElementById('chat-container').appendChild(d); document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight; }
        function renderC() { document.getElementById('chat-container').innerHTML = ""; history.forEach(m => addUI(m.content, m.role)); }
        
        document.getElementById('openSidebar').onclick = () => document.getElementById('sidebar').classList.add('open'); document.getElementById('closeSidebar').onclick = () => document.getElementById('sidebar').classList.remove('open'); document.getElementById('newChatBtn').onclick = startN; document.getElementById('openSettings').onclick = () => document.getElementById('settingsModal').classList.add('active'); document.getElementById('closeSettings').onclick = () => document.getElementById('settingsModal').classList.remove('active'); document.getElementById('closePreview').onclick = () => document.getElementById('previewModal').classList.remove('active');
        
        // --- YENİ AYAR KAYDETME MANTIĞI ---
        document.getElementById('tRange').oninput = (e) => { config.temperature = parseFloat(e.target.value); document.getElementById('tVal').innerText = config.temperature; localStorage.setItem('temp', config.temperature); };
        document.getElementById('savePromptBtn').onclick = () => {
            const newPrompt = document.getElementById('sysPromptInput').value.trim();
            localStorage.setItem('savedSystemPrompt', newPrompt);
            config.systemPrompt = newPrompt;
            toast('AI Kimliği başarıyla kaydedildi! Sonraki mesajda aktif olacak.');
        };
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
