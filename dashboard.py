from flask import Flask, render_template_string, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# --- 10 ANAHTARLI ZEKÂ MOTORU ---
API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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"
]
current_key_index = 0
MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = "Sen Legends Master Pro'sun. Vercel UI klonunda Şenol Kocabıyık'a hizmet eden baş mimarsın. Kodlarda v1/v2 versiyonlama yap."

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
        except:
            current_key_index = (current_key_index + 1) % len(API_KEYS)
            attempts += 1
    return jsonify({"answer": "❌ Tüm anahtarların limiti doldu patron!"})

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
    <meta charset="UTF-8">
    <title>Legends Master Pro | Vercel Edition</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>tailwind.config = { darkMode: 'class', theme: { extend: { colors: { vercelBg: '#000000', vercelBorder: '#333333', vercelHover: '#1A1A1A' } } } }</script>
    <style>
        body { background: #000; color: #ededed; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; height: 100dvh; display: flex; overflow: hidden; }
        .glass { background: rgba(0,0,0,0.8); backdrop-filter: blur(20px); }
        .sidebar { width: 280px; background: #000; border-right: 1px solid var(--vercelBorder); transition: transform 0.3s; display: flex; flex-direction: column; }
        .msg-user { background: #1A1A1A; border: 1px solid var(--vercelBorder); border-radius: 12px; padding: 16px; margin-left: auto; max-width: 85%; }
        .msg-ai { padding: 16px 0; max-width: 100%; border-bottom: 1px solid var(--vercelBorder); display: flex; gap: 16px; }
        
        /* ÖZEL MARKDOWN KOD BLOKLARI */
        .markdown-body pre { background: #0A0A0A !important; border: 1px solid var(--vercelBorder); border-radius: 8px; padding: 45px 16px 16px 16px; margin: 16px 0; position: relative; overflow-x: auto; }
        .code-actions { position: absolute; top: 10px; right: 10px; display: flex; gap: 8px; opacity: 0; transition: opacity 0.2s; }
        .markdown-body pre:hover .code-actions { opacity: 1; }
        .code-btn { padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer; border: 1px solid var(--vercelBorder); transition: 0.2s; }
        .btn-update { background: #2563eb; color: white; border-color: #1d4ed8; }
        .btn-copy { background: #1A1A1A; color: white; }
        .btn-preview { background: #16a34a; color: white; border-color: #15803d; }
        
        .modal { display: none; position: fixed; inset: 0; z-index: 5000; background: rgba(0,0,0,0.9); align-items: center; justify-content: center; padding: 20px; }
        .modal.active { display: flex; }
        .typing-dot { width: 6px; height: 6px; background: white; border-radius: 50%; animation: typing 1s infinite; display: inline-block; margin: 0 2px;}
        @keyframes typing { 0%, 100% { opacity: 0.3; transform:translateY(0); } 50% { opacity: 1; transform:translateY(-3px); } }
        @media (max-width: 768px) { .sidebar { position: absolute; transform: translateX(-100%); z-index: 100; height: 100%; } .sidebar.open { transform: translateX(0); } }
    </style>
</head>
<body>

    <div id="auth-screen" class="fixed inset-0 z-[9999] bg-[#000] flex items-center justify-center p-6">
        <div class="border border-[#333] bg-[#0A0A0A] p-10 rounded-2xl w-full max-w-sm text-center">
            <i class="fas fa-cube text-5xl text-white mb-6"></i>
            <h1 class="text-2xl font-bold mb-8">LEGENDS PRO</h1>
            <input type="email" id="authEmail" class="w-full p-4 mb-4 rounded-xl bg-[#111] border border-[#333] outline-none text-sm focus:border-white transition" placeholder="Email Address">
            <input type="password" id="authPass" class="w-full p-4 mb-6 rounded-xl bg-[#111] border border-[#333] outline-none text-sm focus:border-white transition" placeholder="Password">
            <button id="btnLogin" class="w-full p-4 bg-white text-black rounded-xl font-bold mb-4 hover:bg-gray-200 transition">Log In</button>
            <div class="flex items-center gap-4 opacity-30 mb-4"><hr class="flex-1"><span>OR</span><hr class="flex-1"></div>
            <button id="btnGoogle" class="w-full p-4 bg-[#111] border border-[#333] text-white rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-[#1A1A1A] transition">
                <i class="fab fa-google"></i> Continue with Google
            </button>
        </div>
    </div>

    <aside id="sidebar" class="sidebar">
        <div class="p-4 flex items-center justify-between border-b border-[#333]">
            <span class="font-bold tracking-tight text-white flex items-center gap-2"><i class="fas fa-cube"></i> LEGENDS</span>
            <button id="closeSidebar" class="md:hidden text-gray-400"><i class="fas fa-times"></i></button>
        </div>
        <div class="p-4">
            <button id="newChatBtn" class="w-full text-left p-3 rounded-lg hover:bg-[#1A1A1A] border border-[#333] flex items-center gap-2 text-sm transition text-white">
                <i class="fas fa-pen text-xs"></i> New Chat
            </button>
        </div>
        <div id="historyList" class="flex-1 overflow-y-auto px-2 space-y-1 text-sm text-gray-400">
            </div>
        <div class="p-4 border-t border-[#333] flex items-center justify-between">
            <div class="flex items-center gap-2 text-sm truncate max-w-[150px]" id="userEmailDisplay">
                <div class="w-7 h-7 rounded-full bg-white text-black flex items-center justify-center font-bold text-xs" id="userAvatar">Ş</div>
                <span>Patron</span>
            </div>
            <button id="openSettings" class="text-gray-400 hover:text-white transition"><i class="fas fa-cog"></i></button>
        </div>
    </aside>

    <main class="flex-1 flex flex-col relative h-full">
        <header class="h-14 flex items-center justify-between px-4 border-b border-[#333] md:hidden">
            <button id="openSidebar" class="text-gray-400"><i class="fas fa-bars"></i></button>
            <span class="font-bold text-white flex items-center gap-2"><i class="fas fa-cube"></i> LEGENDS</span>
            <div class="w-6 h-6"></div>
        </header>

        <div id="chat-container" class="flex-1 overflow-y-auto p-4 md:p-8 pb-32 space-y-6">
            <div class="flex flex-col items-center justify-center h-full text-center text-gray-400">
                <i class="fas fa-cube text-5xl mb-6 text-white opacity-20"></i>
                <h2 class="text-2xl font-medium text-white mb-2">How can I help you today?</h2>
                <p class="text-sm">Legends Master Pro - v20.0 Ultimate</p>
            </div>
        </div>

        <div class="absolute bottom-0 w-full p-4 md:p-8 bg-gradient-to-t from-black via-black to-transparent">
            <div class="max-w-3xl mx-auto bg-[#0A0A0A] border border-[#333] rounded-2xl p-2 flex items-end gap-2 shadow-[0_0_30px_rgba(0,0,0,0.8)] focus-within:border-[#555] transition-colors">
                <button class="p-3 text-gray-400 hover:text-white transition rounded-xl"><i class="fas fa-paperclip"></i></button>
                <textarea id="userInput" class="flex-1 bg-transparent border-none text-white resize-none max-h-[200px] py-3 text-sm focus:outline-none" placeholder="Message Legends..." rows="1"></textarea>
                <button id="sendBtn" class="p-3 bg-white text-black rounded-xl hover:bg-gray-200 transition mb-0.5"><i class="fas fa-arrow-up"></i></button>
            </div>
            <div class="text-center text-[10px] text-gray-500 mt-3">Legends AI can make mistakes. Verify important information.</div>
        </div>
    </main>

    <div id="settingsModal" class="modal glass">
        <div class="bg-[#0A0A0A] border border-[#333] p-8 rounded-2xl w-full max-w-md">
            <div class="flex justify-between items-center mb-6"><h2 class="text-xl font-bold">Settings</h2><i class="fas fa-times cursor-pointer text-gray-400" id="closeSettings"></i></div>
            <div class="space-y-6">
                <div>
                    <label class="flex justify-between text-xs font-bold text-gray-400 mb-2 uppercase"><span>Temperature</span><span id="tempVal">0.2</span></label>
                    <input type="range" id="tempRange" min="0" max="1" step="0.1" value="0.2" class="w-full accent-white h-1 bg-[#333] rounded-full appearance-none">
                </div>
                <div class="p-6 border border-[#333] bg-[#111] rounded-xl text-center">
                    <h3 class="font-bold text-white mb-2"><i class="fas fa-database text-blue-500 mr-2"></i>AI Training</h3>
                    <p class="text-xs text-gray-400 mb-4">Upload custom data for embeddings.</p>
                    <button class="w-full p-3 bg-white text-black rounded-lg text-sm font-bold hover:bg-gray-200">Upload Data</button>
                </div>
                <button id="btnLogout" class="w-full p-3 border border-red-900 text-red-500 rounded-lg text-sm font-bold hover:bg-red-900/30">Log Out</button>
            </div>
        </div>
    </div>

    <div id="previewModal" class="modal glass">
        <div class="bg-black border border-[#333] w-[95%] h-[90vh] rounded-2xl overflow-hidden flex flex-col">
            <div class="p-4 flex justify-between items-center border-b border-[#333] bg-[#0A0A0A]">
                <div class="flex gap-2"><div class="w-3 h-3 rounded-full bg-red-500"></div><div class="w-3 h-3 rounded-full bg-yellow-500"></div><div class="w-3 h-3 rounded-full bg-green-500"></div><span class="ml-4 text-xs font-bold text-gray-400">LIVE PREVIEW</span></div>
                <i class="fas fa-times cursor-pointer text-gray-400" id="closePreview"></i>
            </div>
            <iframe id="previewFrame" class="flex-1 w-full bg-white"></iframe>
        </div>
    </div>

    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
        import { getAuth, signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut, setPersistence, browserLocalPersistence } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
        import { getFirestore, collection, doc, setDoc, getDoc, updateDoc, deleteDoc, query, orderBy, onSnapshot, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

        const fConfig = { apiKey: "AIzaSyAnNzL2wSLEsy6DprleCNSq9elnv3X7BTg", authDomain: "legendsai-3e2d6.firebaseapp.com", projectId: "legendsai-3e2d6", storageBucket: "legendsai-3e2d6.firebasestorage.app", messagingSenderId: "504400540515", appId: "1:504400540515:web:16cdc9ff57dd8fa2981956" };
        const app = initializeApp(fConfig); const auth = getAuth(app); const db = getFirestore(app);
        setPersistence(auth, browserLocalPersistence);

        let currentUser = null, currentChatId = null, chatHistory = [], config = { temperature: 0.2 };

        // 4️⃣ MARKDOWN KONTROLLERİ (Butonların görünmesi için özel ayar)
        const renderer = new marked.Renderer();
        renderer.code = function(code, language) {
            const escapedCode = code.replace(/`/g, '\\`').replace(/'/g, "\\'").replace(/"/g, '&quot;');
            return `
            <div class="relative group">
                <div class="code-actions z-10">
                    <button onclick="window.updateCode(\`${escapedCode}\`)" class="code-btn btn-update"><i class="fas fa-history"></i> v2</button>
                    <button onclick="window.copyCode(\`${escapedCode}\`, this)" class="code-btn btn-copy"><i class="fas fa-copy"></i> Kopyala</button>
                    <button onclick="window.previewCode(\`${escapedCode}\`)" class="code-btn btn-preview"><i class="fas fa-play"></i> Önizle</button>
                </div>
                <pre><code class="language-${language}">${code}</code></pre>
            </div>`;
        };
        marked.setOptions({ renderer: renderer });

        window.updateCode = (code) => { 
            const vCount = chatHistory.filter(m => m.content.includes("\`\`\`")).length + 1;
            document.getElementById('userInput').value = `Mevcut kodu bozmadan şu özellikleri ekle (v${vCount}):\\n\\n\`\`\`\\n${code}\\n\`\`\``; 
            document.getElementById('userInput').focus(); 
        };
        window.copyCode = (code, btn) => { navigator.clipboard.writeText(code); btn.innerHTML = '<i class="fas fa-check text-green-400"></i>'; setTimeout(() => btn.innerHTML = '<i class="fas fa-copy"></i> Kopyala', 2000); };
        window.previewCode = (code) => { document.getElementById('previewModal').classList.add('active'); document.getElementById('previewFrame').srcdoc = code; };

        // AUTH KONTROLÜ
        onAuthStateChanged(auth, (u) => {
            if(u){
                currentUser = u; document.getElementById('auth-screen').style.display = 'none';
                document.getElementById('userEmailDisplay').innerHTML = `<div class="w-7 h-7 rounded-full bg-white text-black flex items-center justify-center font-bold text-xs">${u.email[0].toUpperCase()}</div><span class="truncate">${u.email.split('@')[0]}</span>`;
                syncHistory(); startNewChat();
            } else { document.getElementById('auth-screen').style.display = 'flex'; }
        });

        document.getElementById('btnLogin').onclick = () => signInWithEmailAndPassword(auth, document.getElementById('authEmail').value, document.getElementById('authPass').value).catch(e => alert(e.message));
        document.getElementById('btnGoogle').onclick = () => signInWithPopup(auth, new GoogleAuthProvider());
        document.getElementById('btnLogout').onclick = () => { signOut(auth); document.getElementById('settingsModal').classList.remove('active'); };

        // GEÇMİŞ
        function syncHistory() {
            const q = query(collection(db, `users/${currentUser.uid}/chats`), orderBy('updatedAt', 'desc'));
            onSnapshot(q, (snap) => {
                const list = document.getElementById('historyList'); list.innerHTML = "";
                snap.forEach(d => {
                    const active = currentChatId === d.id;
                    const div = document.createElement('div');
                    div.className = `p-3 rounded-lg cursor-pointer flex justify-between items-center group transition ${active ? 'bg-[#1A1A1A] text-white' : 'hover:bg-[#111]'}`;
                    div.innerHTML = `<span class="truncate pr-2">${d.data().title || 'New Chat'}</span><i class="fas fa-trash-alt opacity-0 group-hover:opacity-50 hover:text-red-500" onclick="event.stopPropagation(); deleteChat('${d.id}')"></i>`;
                    div.onclick = () => loadChat(d.id); list.appendChild(div);
                });
            });
        }

        async function startNewChat() {
            currentChatId = "chat_" + Date.now(); chatHistory = [];
            document.getElementById('chat-container').innerHTML = '<div class="flex flex-col items-center justify-center h-full text-center text-gray-400"><i class="fas fa-cube text-5xl mb-6 text-white opacity-20"></i><h2 class="text-2xl font-medium text-white mb-2">How can I help you today?</h2><p class="text-sm">Legends Master Pro - v20.0</p></div>';
            await setDoc(doc(db, `users/${currentUser.uid}/chats`, currentChatId), { title: "New Chat", updatedAt: serverTimestamp(), messages: [] });
        }

        async function loadChat(id) {
            currentChatId = id; const d = await getDoc(doc(db, `users/${currentUser.uid}/chats`, id));
            if(d.exists()){ chatHistory = d.data().messages || []; renderChat(); }
        }
        window.deleteChat = async (id) => { if(confirm("Delete this chat?")) { await deleteDoc(doc(db, `users/${currentUser.uid}/chats`, id)); startNewChat(); } };

// MESAJ GÖNDERME
        document.getElementById('sendBtn').onclick = sendMessage;
        document.getElementById('userInput').oninput = function() { this.style.height = 'auto'; this.style.height = this.scrollHeight + 'px'; };
        document.getElementById('userInput').onkeydown = (e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } };

        async function sendMessage() {
            const val = document.getElementById('userInput').value.trim(); if(!val) return;
            if(chatHistory.length === 0) document.getElementById('chat-container').innerHTML = '';
            
            document.getElementById('userInput').value = ""; document.getElementById('userInput').style.height = 'auto';
            addMsgUI(val, 'user'); chatHistory.push({role: "user", content: val});
            
            const loadId = "ai_" + Date.now();
            document.getElementById('chat-container').innerHTML += `<div id="${loadId}" class="msg-ai text-gray-400 text-sm"><div class="w-8 h-8 rounded-full border border-[#333] flex items-center justify-center flex-shrink-0 bg-white"><i class="fas fa-cube text-xs text-black"></i></div><div class="flex items-center"><div class="typing-dot"></div><div class="typing-dot" style="animation-delay:0.2s"></div><div class="typing-dot" style="animation-delay:0.4s"></div></div></div>`;
            document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;

            try {
                const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ messages: chatHistory, settings: config }) });
                const data = await res.json();
                document.getElementById(loadId).remove();
                addMsgUI(data.answer, 'assistant'); chatHistory.push({role: "assistant", content: data.answer});
                await updateDoc(doc(db, `users/${currentUser.uid}/chats`, currentChatId), { title: chatHistory[0].content.substring(0, 30), messages: chatHistory, updatedAt: serverTimestamp() });
            } catch(e) { document.getElementById(loadId).innerHTML = "❌ Connection Error"; }
        }

        function addMsgUI(t, r) {
            const d = document.createElement('div'); d.className = r === 'user' ? 'msg-user text-sm' : 'msg-ai text-sm';
            if(r === 'user') d.innerHTML = t;
            else d.innerHTML = `<div class="w-8 h-8 rounded-full border border-[#333] flex items-center justify-center flex-shrink-0 bg-white"><i class="fas fa-cube text-xs text-black"></i></div><div class="flex-1 markdown-body text-[#ededed] leading-relaxed break-words overflow-hidden w-full max-w-[calc(100vw-80px)] md:max-w-full">${marked.parse(t)}</div>`;
            document.getElementById('chat-container').appendChild(d);
            document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
        }
        function renderChat() { document.getElementById('chat-container').innerHTML = ""; chatHistory.forEach(m => addMsgUI(m.content, m.role)); }

        // UI KONTROLLERİ
        document.getElementById('openSidebar').onclick = () => document.getElementById('sidebar').classList.add('open');
        document.getElementById('closeSidebar').onclick = () => document.getElementById('sidebar').classList.remove('open');
        document.getElementById('newChatBtn').onclick = startNewChat;
        document.getElementById('openSettings').onclick = () => document.getElementById('settingsModal').classList.add('active');
        document.getElementById('closeSettings').onclick = () => document.getElementById('settingsModal').classList.remove('active');
        document.getElementById('closePreview').onclick = () => document.getElementById('previewModal').classList.remove('active');
        document.getElementById('tempRange').oninput = (e) => { document.getElementById('tempVal').innerText = e.target.value; config.temperature = parseFloat(e.target.value); };
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
