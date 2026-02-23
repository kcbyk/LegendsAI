from flask import Flask, render_template_string, request, jsonify
import requests, json, os
from openai import OpenAI

app = Flask(__name__)

# --- LEGENDS AI V11 CORE (1 MİLYON TOKEN KAPASİTESİ) ---
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
SYSTEM_PROMPT = "Sen Legends AI'sın. Şenol'un baş yazılım mimarısın. 1) Sadece kod yaz. 2) Asla yarıda kesme. 3) Tek HTML dosyasında kusursuz iş çıkar."

# --- PWA GEREKLİLİKLERİ ---
@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Legends AI | Master",
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

# --- ANA ARAYÜZ (FİREBASE ENTEGRELİ) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>LEGENDS AI | CLOUD</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
    <link rel="manifest" href="/manifest.json">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root { --primary: #f97316; --bg: #020617; --card: rgba(15, 23, 42, 0.85); }
        body { background: var(--bg); color: #f1f5f9; font-family: 'Inter', sans-serif; height: 100dvh; overflow: hidden; margin: 0; display: flex; flex-direction: column; }
        .glass { background: var(--card); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.08); }
        
        /* AUTH SCREEN */
        #auth-screen { position: absolute; inset: 0; z-index: 200; display: flex; flex-direction: column; justify-content: center; align-items: center; background: var(--bg); padding: 20px; }
        .auth-box { width: 100%; max-width: 350px; padding: 30px; border-radius: 30px; display: flex; flex-direction: column; gap: 15px; }
        .auth-input { width: 100%; padding: 14px; border-radius: 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; outline: none; }
        .auth-btn { width: 100%; padding: 14px; border-radius: 12px; font-weight: bold; background: var(--primary); color: white; cursor: pointer; }
        .google-btn { background: white; color: black; display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 10px; }

        /* SIDEBAR */
        #sidebar { position: absolute; left: -300px; top: 0; bottom: 0; width: 280px; z-index: 150; transition: 0.3s; display: flex; flex-direction: column; }
        #sidebar.open { left: 0; }
        .chat-item { padding: 12px 15px; border-radius: 10px; margin-bottom: 8px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); }
        .chat-item:hover, .chat-item.active { background: rgba(249, 115, 22, 0.2); border-left: 3px solid var(--primary); }
        
        /* CHAT AREA */
        header { padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; z-index: 50; border-bottom: 1px solid rgba(255,255,255,0.05); }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; scroll-behavior: smooth; }
        .msg { max-width: 92%; padding: 16px 20px; border-radius: 24px; line-height: 1.6; font-size: 15px; animation: slideIn 0.3s ease; }
        .msg-user { align-self: flex-end; background: var(--primary); color: white; border-bottom-right-radius: 4px; }
        .msg-ai { align-self: flex-start; background: rgba(30, 41, 59, 0.7); border-bottom-left-radius: 4px; width: 100%; }
        
        .input-area { padding: 16px; padding-bottom: max(16px, env(safe-area-inset-bottom)); }
        .input-box { border-radius: 28px; padding: 8px 8px 8px 18px; display: flex; align-items: flex-end; gap: 12px; }
        textarea { flex: 1; background: transparent; border: none; outline: none; color: white; max-height: 140px; resize: none; font-size: 16px; padding: 10px 0; }
        .circle-btn { width: 48px; height: 48px; border-radius: 50%; display: flex; justify-content: center; align-items: center; cursor: pointer; background: var(--primary); color: white; }
        
        pre { background: #000 !important; border-radius: 16px; padding: 14px; margin: 10px 0; overflow-x: auto; border: 1px solid rgba(255,255,255,0.05); }
        code { font-family: 'Fira Code', monospace; font-size: 13px; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        #overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.5); z-index: 140; display: none; }
    </style>
</head>
<body>

    <div id="auth-screen">
        <div class="text-center mb-8"><i class="fas fa-crown text-5xl text-orange-500 mb-4 drop-shadow-[0_0_15px_rgba(249,115,22,0.5)]"></i><h1 class="text-3xl font-black">LEGENDS AI</h1><p class="text-gray-400 text-sm mt-2">Giriş Yap veya Kayıt Ol</p></div>
        <div class="auth-box glass">
            <input type="email" id="email" class="auth-input" placeholder="E-Posta">
            <input type="password" id="password" class="auth-input" placeholder="Şifre">
            <button id="btnLogin" class="auth-btn">GİRİŞ YAP</button>
            <button id="btnRegister" class="auth-btn bg-gray-700">KAYIT OL</button>
            <div class="text-center text-xs text-gray-500 my-2">VEYA</div>
            <button id="btnGoogle" class="auth-btn google-btn"><img src="https://cdn-icons-png.flaticon.com/512/300/300221.png" width="20"> Google ile Devam Et</button>
        </div>
    </div>

    <div id="app-screen" class="hidden h-full flex flex-col w-full relative">
        <header class="glass">
            <button id="menuBtn" class="text-xl text-white"><i class="fas fa-bars"></i></button>
            <div class="font-black text-lg flex items-center gap-2"><i class="fas fa-crown text-orange-500"></i> LEGENDS</div>
            <button id="newChatTopBtn" class="text-orange-500 text-xl"><i class="fas fa-plus-circle"></i></button>
        </header>

        <div id="chat-container"></div>

        <div class="input-area">
            <div class="input-box glass">
                <textarea id="userInput" placeholder="Yazılım emrini ver..." rows="1" oninput="this.style.height='auto';this.style.height=this.scrollHeight+'px'"></textarea>
                <div id="sendBtn" class="circle-btn"><i class="fas fa-paper-plane"></i></div>
            </div>
        </div>
    </div>

    <div id="overlay"></div>
    <aside id="sidebar" class="glass border-r border-white/5 p-4">
        <div class="flex items-center gap-3 mb-6 p-2">
            <div class="w-10 h-10 rounded-full bg-orange-500 flex items-center justify-center font-bold text-lg" id="userAvatar">A</div>
            <div class="flex-1 overflow-hidden"><div class="text-sm font-bold truncate" id="userName">Kullanıcı</div><div class="text-[10px] text-green-400">Çevrimiçi</div></div>
        </div>
        <button id="newChatSidebarBtn" class="w-full py-3 bg-orange-500/20 text-orange-500 rounded-xl font-bold mb-4 flex items-center justify-center gap-2 hover:bg-orange-500/40 transition"><i class="fas fa-plus"></i> YENİ SOHBET</button>
        <div class="text-[10px] text-gray-500 font-bold mb-2 uppercase">Geçmiş Sohbetler</div>
        <div id="chatHistoryList" class="flex-1 overflow-y-auto"></div>
        <button id="btnLogout" class="mt-4 p-3 bg-red-500/20 text-red-500 rounded-xl text-sm font-bold"><i class="fas fa-sign-out-alt"></i> ÇIKIŞ YAP</button>
    </aside>

    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
        import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
        import { getFirestore, collection, doc, setDoc, getDoc, getDocs, updateDoc, deleteDoc, serverTimestamp, query, orderBy } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

        // PATRONUN FİREBASE ANAHTARLARI
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

        let currentUser = null;
        let currentChatId = null;
        let currentMessages = [];

        // DOM ELEMENTS
        const authScreen = document.getElementById('auth-screen');
        const appScreen = document.getElementById('app-screen');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        const chatContainer = document.getElementById('chat-container');
        const chatList = document.getElementById('chatHistoryList');
        const userInput = document.getElementById('userInput');

        // --- AUTH LOGIC ---
        onAuthStateChanged(auth, (user) => {
            if (user) {
                currentUser = user;
                document.getElementById('userName').innerText = user.displayName || user.email.split('@')[0];
                document.getElementById('userAvatar').innerText = (user.displayName || user.email)[0].toUpperCase();
                authScreen.style.display = 'none';
                appScreen.classList.remove('hidden');
                loadChats();
                startNewChat();
            } else {
                currentUser = null;
                authScreen.style.display = 'flex';
                appScreen.classList.add('hidden');
            }
        });

        document.getElementById('btnLogin').onclick = () => {
            const e = document.getElementById('email').value, p = document.getElementById('password').value;
            signInWithEmailAndPassword(auth, e, p).catch(err => alert("Hata: " + err.message));
        };
        
        document.getElementById('btnRegister').onclick = () => {
            const e = document.getElementById('email').value, p = document.getElementById('password').value;
            createUserWithEmailAndPassword(auth, e, p).catch(err => alert("Hata: " + err.message));
        };

        document.getElementById('btnGoogle').onclick = () => {
            signInWithPopup(auth, new GoogleAuthProvider()).catch(err => alert("Hata: " + err.message));
        };

        document.getElementById('btnLogout').onclick = () => { signOut(auth); sidebar.classList.remove('open'); overlay.style.display = 'none'; };

        // --- UI LOGIC ---
        document.getElementById('menuBtn').onclick = () => { sidebar.classList.add('open'); overlay.style.display = 'block'; };
        overlay.onclick = () => { sidebar.classList.remove('open'); overlay.style.display = 'none'; };

        document.getElementById('newChatTopBtn').onclick = () => { startNewChat(); };
        document.getElementById('newChatSidebarBtn').onclick = () => { startNewChat(); sidebar.classList.remove('open'); overlay.style.display='none'; };

        // --- DATABASE LOGIC ---
        function generateId() { return Date.now().toString(36) + Math.random().toString(36).substr(2); }

        async function loadChats() {
            chatList.innerHTML = '<div class="text-center text-xs text-gray-500 mt-4">Yükleniyor...</div>';
            const q = query(collection(db, `users/${currentUser.uid}/chats`), orderBy('updatedAt', 'desc'));
            const snap = await getDocs(q);
            chatList.innerHTML = '';
            snap.forEach(doc => {
                const data = doc.data();
                const div = document.createElement('div');
                div.className = `chat-item ${currentChatId === doc.id ? 'active' : ''}`;
                div.innerHTML = `<span class="truncate text-sm flex-1">${data.title || 'Yeni Sohbet'}</span><i class="fas fa-trash text-gray-500 hover:text-red-500 ml-2" onclick="event.stopPropagation(); deleteChat('${doc.id}')"></i>`;
                div.onclick = () => { loadSpecificChat(doc.id); sidebar.classList.remove('open'); overlay.style.display='none'; };
                chatList.appendChild(div);
            });
        }

        async function startNewChat() {
            currentChatId = generateId();
            currentMessages = [];
            chatContainer.innerHTML = '<div class="msg msg-ai glass"><b>Legends AI:</b> Bağlantı sağlandı. Senin ve ekibinin emrindeyim.</div>';
            await setDoc(doc(db, `users/${currentUser.uid}/chats`, currentChatId), {
                title: "Yeni Sohbet", updatedAt: serverTimestamp(), messages: []
            });
            loadChats();
        }

        async function loadSpecificChat(chatId) {
            currentChatId = chatId;
            chatContainer.innerHTML = '';
            const docSnap = await getDoc(doc(db, `users/${currentUser.uid}/chats`, chatId));
            if (docSnap.exists()) {
                currentMessages = docSnap.data().messages || [];
                if(currentMessages.length === 0) chatContainer.innerHTML = '<div class="msg msg-ai glass"><b>Legends AI:</b> Bağlantı sağlandı.</div>';
                currentMessages.forEach(m => addChatUI(m.content, m.role));
            }
            loadChats();
        }

        window.deleteChat = async function(chatId) { // window. attach for inline onclick
            if(confirm("Sohbeti silmek istiyor musun?")) {
                await deleteDoc(doc(db, `users/${currentUser.uid}/chats`, chatId));
                if(currentChatId === chatId) startNewChat(); else loadChats();
            }
        }

        // --- CHAT SYSTEM ---
        document.getElementById('sendBtn').onclick = sendMsg;
        userInput.addEventListener('keypress', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMsg(); } });

        async function sendMsg() {
            const val = userInput.value.trim(); if(!val) return;
            userInput.value = ""; userInput.style.height = 'auto';
            
            // Add to UI
            addChatUI(val, 'user');
            const loadId = 'ai-' + Date.now(); addLoadingUI(loadId);
            
            // Save to memory
            currentMessages.push({role: "user", content: val});
            
            // Update Title if first message
            let chatTitle = currentMessages[0].content.substring(0, 25);
            
            // Save to DB (User message)
            await updateDoc(doc(db, `users/${currentUser.uid}/chats`, currentChatId), {
                title: chatTitle, messages: currentMessages, updatedAt: serverTimestamp()
            });
            loadChats(); // Refresh sidebar

            // Send to Flask Backend (which forwards to Groq)
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ messages: currentMessages })
                });
                const data = await res.json();
                
                // Remove loading, Add AI response to UI
                document.getElementById(loadId).remove();
                addChatUI(data.answer, 'assistant');
                
                // Save AI response to memory & DB
                currentMessages.push({role: "assistant", content: data.answer});
                await updateDoc(doc(db, `users/${currentUser.uid}/chats`, currentChatId), {
                    messages: currentMessages, updatedAt: serverTimestamp()
                });

            } catch(e) { 
                document.getElementById(loadId).innerText = "❌ Sunucu bağlantı hatası!"; 
            }
        }

        function addChatUI(text, role) {
            const d = document.createElement('div');
            d.className = `msg msg-${role === 'user' ? 'user' : 'ai'} glass`;
            d.innerHTML = role === 'user' ? text : marked.parse(text);
            chatContainer.appendChild(d);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function addLoadingUI(id) {
            const d = document.createElement('div');
            d.className = `msg msg-ai glass`; d.id = id;
            d.innerHTML = `<span class="animate-pulse opacity-75">Legends AI Düşünüyor...</span>`;
            chatContainer.appendChild(d);
            chatContainer.scrollTop = chatContainer.scrollHeight;
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
    
    # Frontend'den gelen o sohbete ait mesaj geçmişi
    incoming_messages = data.get('messages', [])
    
    # Legends AI'ın karakterini başa ekliyoruz
    system_msg = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages_for_llm = system_msg + incoming_messages

    success = False
    answer = "Hata"
    
    # 10 Motorlu Rotasyon Sistemi
    while current_key_index < len(API_KEYS):
        try:
            client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=API_KEYS[current_key_index])
            res = client.chat.completions.create(
                model=MODEL, 
                messages=messages_for_llm, 
                temperature=0.2
            )
            answer = res.choices[0].message.content
            success = True
            break
        except Exception as e: 
            print("Anahtar Hatası, sıradakine geçiliyor...")
            current_key_index += 1
            
    if not success: answer = "❌ Limit doldu! Lütfen daha sonra tekrar deneyin."

    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

