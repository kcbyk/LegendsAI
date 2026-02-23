from flask import Flask, render_template_string, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# --- LEGENDS AI V12 KUSURSUZ CORE ---
API_KEYS = [
    "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",
    "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",
    "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"
] # Güvenlik için listeyi kısalttım, sen kendi tam listeni buraya koyarsın

current_key_index = 0
MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = "Sen Legends AI'sın. Şenol'un baş yazılım mimarısın. 1) Sadece kod yaz. 2) Asla yarıda kesme. 3) Tek HTML dosyasında kusursuz iş çıkar. 4) Yazdığın kodun en altına, nasıl kurulacağını adım adım anlat."

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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>LEGENDS AI | MASTER</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
    <link rel="manifest" href="/manifest.json">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        /* TEMA AYARLARI */
        :root { --primary: #f97316; --bg: #020617; --card: rgba(15, 23, 42, 0.85); --text: #f1f5f9; }
        .theme-light { --primary: #ea580c; --bg: #f8fafc; --card: #ffffff; --text: #0f172a; }
        .theme-hacker { --primary: #22c55e; --bg: #000000; --card: rgba(0, 20, 0, 0.8); --text: #22c55e; }
        
        body { background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; height: 100dvh; overflow: hidden; margin: 0; display: flex; flex-direction: column; transition: 0.3s; }
        .glass { background: var(--card); backdrop-filter: blur(20px); border: 1px solid rgba(128, 128, 128, 0.1); color: var(--text); }
        
        #auth-screen { position: absolute; inset: 0; z-index: 200; display: flex; flex-direction: column; justify-content: center; align-items: center; background: var(--bg); padding: 20px; }
        .auth-box { width: 100%; max-width: 350px; padding: 30px; border-radius: 30px; display: flex; flex-direction: column; gap: 15px; }
        .auth-input { width: 100%; padding: 14px; border-radius: 12px; background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.2); color: var(--text); outline: none; }
        .auth-btn { width: 100%; padding: 14px; border-radius: 12px; font-weight: bold; background: var(--primary); color: white; cursor: pointer; transition: 0.2s; }
        .google-btn { background: white; color: black; display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 10px; }
        
        #sidebar { position: absolute; left: -300px; top: 0; bottom: 0; width: 280px; z-index: 150; transition: 0.3s; display: flex; flex-direction: column; }
        #sidebar.open { left: 0; }
        .chat-item { padding: 12px 15px; border-radius: 10px; margin-bottom: 8px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
        .chat-item:hover, .chat-item.active { background: rgba(128,128,128,0.1); border-left: 3px solid var(--primary); }
        
        header { padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; z-index: 50; border-bottom: 1px solid rgba(128,128,128,0.1); }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; scroll-behavior: smooth; }
        .msg { max-width: 92%; padding: 16px 20px; border-radius: 24px; line-height: 1.6; font-size: 15px; }
        .msg-user { align-self: flex-end; background: var(--primary); color: white; border-bottom-right-radius: 4px; }
        .msg-ai { align-self: flex-start; background: var(--card); border: 1px solid rgba(128,128,128,0.1); border-bottom-left-radius: 4px; width: 100%; overflow-x: hidden; }
        
        .input-area { padding: 16px; padding-bottom: max(16px, env(safe-area-inset-bottom)); position: relative; }
        .input-box { border-radius: 28px; padding: 8px 8px 8px 12px; display: flex; align-items: flex-end; gap: 10px; }
        .attach-btn { padding: 10px; cursor: pointer; font-size: 20px; transition: 0.2s; color: var(--text); opacity: 0.7; }
        .attach-btn:hover { color: var(--primary); opacity: 1; }
        textarea { flex: 1; background: transparent; border: none; outline: none; color: var(--text); max-height: 140px; resize: none; font-size: 16px; padding: 10px 0; }
        .circle-btn { width: 44px; height: 44px; border-radius: 50%; display: flex; justify-content: center; align-items: center; cursor: pointer; background: var(--primary); color: white; flex-shrink: 0; }
        
        /* ACTION MENU (GERİ GELDİ VE ÇALIŞIYOR) */
        #actionMenu { display: none; position: absolute; bottom: 80px; left: 20px; flex-direction: column; gap: 5px; padding: 10px; border-radius: 16px; min-width: 170px; z-index: 100; }
        #actionMenu.show { display: flex; }
        .action-item { display: flex; align-items: center; gap: 10px; padding: 12px; cursor: pointer; border-radius: 10px; font-size: 14px; color: var(--text); }
        .action-item:hover { background: rgba(128,128,128,0.1); color: var(--primary); }

        /* KOD BLOKLARI VE 3 BUTON YAN YANA */
        pre { background: #0f172a !important; color: #e2e8f0; border-radius: 16px; padding: 50px 14px 14px 14px; margin: 15px 0; position: relative; max-width: 100%; overflow-x: auto; border: 1px solid #334155; }
        code { font-family: 'Fira Code', monospace; font-size: 13px; }
        .code-actions { position: absolute; top: 8px; right: 8px; display: flex; gap: 6px; z-index: 10; }
        .code-btn { background: #334155; border:none; color: white; padding: 6px 10px; border-radius: 8px; font-size: 12px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 5px; transition: 0.2s; }
        .code-btn:hover { background: var(--primary); }
        .btn-update { background: #1e3a8a; color: #93c5fd; }
        .btn-update:hover { background: #3b82f6; color: white; }
        .btn-preview { background: #14532d; color: #86efac; }
        .btn-preview:hover { background: #22c55e; color: white; }

        /* MODALS */
        .modal-container { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 300; justify-content: center; align-items: center; padding: 20px; }
        .modal-container.show { display: flex; }
        .modal-box { width: 100%; max-width: 500px; max-height: 90vh; display: flex; flex-direction: column; border-radius: 24px; overflow: hidden; }
        .modal-header { padding: 16px 20px; background: rgba(0,0,0,0.5); display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(128,128,128,0.1); }
        .modal-close { font-size: 24px; cursor: pointer; color: white; }
        #previewFrame { flex: 1; width: 100%; background: #fff; border: none; min-height: 400px; }
        
        /* GİZLİ INPUTLAR (DOSYA VE FOTO İÇİN) */
        .hidden-input { display: none; }
        #overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.5); z-index: 140; display: none; }
    </style>
</head>
<body>

    <div id="auth-screen">
        <div class="text-center mb-8"><i class="fas fa-crown text-5xl text-orange-500 mb-4 drop-shadow-[0_0_15px_rgba(249,115,22,0.5)]"></i><h1 class="text-3xl font-black">LEGENDS AI</h1><p class="text-sm mt-2 opacity-70">Sisteme Giriş Yap</p></div>
        <div class="auth-box glass">
            <input type="email" id="email" class="auth-input" placeholder="E-Posta">
            <input type="password" id="password" class="auth-input" placeholder="Şifre">
            <button id="btnLogin" class="auth-btn">GİRİŞ YAP</button>
            <button id="btnRegister" class="auth-btn" style="background: #334155;">KAYIT OL</button>
            <div class="text-center text-xs opacity-50 my-2">VEYA (Sadece Tarayıcılar İçin)</div>
            <button id="btnGoogle" class="auth-btn google-btn"><img src="https://cdn-icons-png.flaticon.com/512/300/300221.png" width="20"> Google ile Devam Et</button>
            <div class="text-[10px] text-center opacity-50 mt-2">APK kullanıyorsanız, lütfen E-Posta ile kayıt olun. Sistem sizi hep hatırlayacaktır.</div>
        </div>
    </div>

    <div id="app-screen" class="hidden h-full flex flex-col w-full relative">
        <header class="glass">
            <button id="menuBtn" class="text-xl p-2"><i class="fas fa-bars"></i></button>
            <div class="font-black text-lg flex items-center gap-2"><i class="fas fa-crown text-orange-500"></i> LEGENDS</div>
            <button id="newChatTopBtn" class="text-orange-500 text-xl p-2"><i class="fas fa-plus-circle"></i></button>
        </header>
        
        <div id="chat-container"></div>
        
        <div class="input-area">
            <div id="actionMenu" class="glass">
                <div class="action-item" onclick="document.getElementById('imgInput').click()"><i class="fas fa-image w-6 text-orange-500"></i> Fotoğraf Ekle</div>
                <div class="action-item" onclick="document.getElementById('fileInput').click()"><i class="fas fa-file-code w-6 text-blue-500"></i> Dosya Aç</div>
                <div class="action-item" id="openSettingsBtn"><i class="fas fa-cogs w-6 text-gray-400"></i> Eğitim/Ayar</div>
            </div>

            <div class="input-box glass">
                <div id="attachBtn" class="attach-btn"><i class="fas fa-plus"></i></div>
                <textarea id="userInput" placeholder="Emrini ver..." rows="1" oninput="this.style.height='auto';this.style.height=this.scrollHeight+'px'"></textarea>
                <div id="sendBtn" class="circle-btn"><i class="fas fa-paper-plane"></i></div>
            </div>
        </div>
    </div>

    <input type="file" id="imgInput" class="hidden-input" accept="image/*">
    <input type="file" id="fileInput" class="hidden-input" accept=".txt,.html,.js,.py,.json">

    <div id="overlay"></div>
    <aside id="sidebar" class="glass border-r border-gray-500/20 p-4">
        <div class="flex items-center gap-3 mb-6 p-2 bg-gray-500/10 rounded-xl">
            <div class="w-10 h-10 rounded-full bg-orange-500 flex items-center justify-center font-bold text-lg text-white" id="userAvatar">A</div>
            <div class="flex-1 overflow-hidden"><div class="text-sm font-bold truncate" id="userName">Kullanıcı</div><div class="text-[10px] text-green-500">Çevrimiçi</div></div>
        </div>
        <button id="newChatSidebarBtn" class="w-full py-3 bg-orange-500 text-white rounded-xl font-bold mb-4 flex items-center justify-center gap-2"><i class="fas fa-plus"></i> YENİ SOHBET</button>
        <div id="chatHistoryList" class="flex-1 overflow-y-auto px-2"></div>
        <button id="btnLogout" class="mt-4 p-3 bg-red-500/20 text-red-500 rounded-xl text-sm font-bold w-full"><i class="fas fa-sign-out-alt"></i> ÇIKIŞ</button>
    </aside>

    <div id="previewModal" class="modal-container">
        <div class="modal-box glass h-full">
            <div class="modal-header">
                <div class="font-bold text-orange-500"><i class="fas fa-play"></i> Canlı Önizleme</div>
                <i class="fas fa-times modal-close" id="closePreviewBtn"></i>
            </div>
            <iframe id="previewFrame"></iframe>
        </div>
    </div>

    <div id="settingsModal" class="modal-container">
        <div class="modal-box glass">
            <div class="modal-header"><div class="font-bold">Ayarlar & Eğitim</div><i class="fas fa-times modal-close" id="closeSettingsBtn"></i></div>
            <div class="p-6 flex flex-col gap-4">
                <div>
                    <label class="block text-sm font-bold mb-2 opacity-70">Uygulama Teması</label>
                    <div class="flex gap-2">
                        <button class="flex-1 p-2 bg-gray-800 text-white rounded-lg border border-gray-600" onclick="document.body.className=''">Karanlık</button>
                        <button class="flex-1 p-2 bg-white text-black rounded-lg border border-gray-300" onclick="document.body.className='theme-light'">Aydınlık</button>
                        <button class="flex-1 p-2 bg-black text-green-500 rounded-lg border border-green-500" onclick="document.body.className='theme-hacker'">Hacker</button>
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-bold mb-2 opacity-70">Yaratıcılık (Temperature)</label>
                    <input type="range" id="tempRange" min="0" max="1" step="0.1" value="0.2" class="w-full">
                </div>
                <button id="saveSettingsBtn" class="auth-btn"><i class="fas fa-check"></i> KAYDET</button>
            </div>
        </div>
    </div>

    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
        import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, GoogleAuthProvider, signInWithRedirect, onAuthStateChanged, signOut, setPersistence, browserLocalPersistence } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
        import { getFirestore, collection, doc, setDoc, getDoc, getDocs, updateDoc, deleteDoc, serverTimestamp, query, orderBy } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

        // FIREBASE ANAHTARLARI
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

        // EN ÖNEMLİSİ: KALICI HAFIZA (BENİ HATIRLA) EKLENDİ
        setPersistence(auth, browserLocalPersistence);

        let currentUser = null; let currentChatId = null; let currentMessages = []; let currentTemperature = 0.2;

        // UI ELEMENTLERİ
        const authScreen = document.getElementById('auth-screen'); const appScreen = document.getElementById('app-screen');
        const sidebar = document.getElementById('sidebar'); const overlay = document.getElementById('overlay');
        const chatContainer = document.getElementById('chat-container'); const chatList = document.getElementById('chatHistoryList');
        const userInput = document.getElementById('userInput'); const actionMenu = document.getElementById('actionMenu');
        const previewModal = document.getElementById('previewModal'); const settingsModal = document.getElementById('settingsModal');

        // DOSYA VE FOTOĞRAF YÜKLEME SİMÜLASYONU
        document.getElementById('imgInput').addEventListener('change', function(e) {
            if(e.target.files[0]) {
                const toast = document.createElement('div'); toast.className = 'fixed bottom-20 left-1/2 -translate-x-1/2 bg-orange-500 text-white px-4 py-2 rounded-full text-sm z-50';
                toast.innerText = '📸 Fotoğraf Seçildi! (Vision API eklendiğinde analiz edilecek)'; document.body.appendChild(toast); setTimeout(() => toast.remove(), 3000);
                actionMenu.classList.remove('show');
            }
        });
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if(file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    userInput.value = "Şu dosyayı analiz et:\n" + e.target.result.substring(0, 500) + "...";
                    actionMenu.classList.remove('show');
                };
                reader.readAsText(file);
            }
        });

        // MENÜLER VE MODALLAR
        document.getElementById('attachBtn').onclick = () => { actionMenu.classList.toggle('show'); };
        window.openPreview = function(code) { previewModal.classList.add('show'); document.getElementById('previewFrame').srcdoc = code; };
        document.getElementById('closePreviewBtn').onclick = () => { previewModal.classList.remove('show'); document.getElementById('previewFrame').srcdoc = ""; };
        document.getElementById('openSettingsBtn').onclick = () => { actionMenu.classList.remove('show'); settingsModal.classList.add('show'); };
        document.getElementById('closeSettingsBtn').onclick = () => { settingsModal.classList.remove('show'); };
        document.getElementById('saveSettingsBtn').onclick = () => { currentTemperature = parseFloat(document.getElementById('tempRange').value); settingsModal.classList.remove('show'); };

// AUTH VE HATIRLAMA SİSTEMİ
        onAuthStateChanged(auth, (user) => {
            if (user) {
                currentUser = user;
                document.getElementById('userName').innerText = user.displayName || user.email.split('@')[0];
                document.getElementById('userAvatar').innerText = (user.displayName || user.email)[0].toUpperCase();
                authScreen.style.display = 'none'; appScreen.classList.remove('hidden'); loadChats(); startNewChat();
            } else { currentUser = null; authScreen.style.display = 'flex'; appScreen.classList.add('hidden'); }
        });

        document.getElementById('btnLogin').onclick = () => { signInWithEmailAndPassword(auth, document.getElementById('email').value, document.getElementById('password').value).catch(err=>alert(err.message)); };
        document.getElementById('btnRegister').onclick = () => { createUserWithEmailAndPassword(auth, document.getElementById('email').value, document.getElementById('password').value).catch(err=>alert(err.message)); };
        document.getElementById('btnGoogle').onclick = () => { signInWithRedirect(auth, new GoogleAuthProvider()).catch(err=>alert(err.message)); };
        document.getElementById('btnLogout').onclick = () => { signOut(auth); sidebar.classList.remove('open'); overlay.style.display='none'; };

        document.getElementById('menuBtn').onclick = () => { sidebar.classList.add('open'); overlay.style.display='block'; };
        overlay.onclick = () => { sidebar.classList.remove('open'); overlay.style.display='none'; };
        document.getElementById('newChatTopBtn').onclick = startNewChat;
        document.getElementById('newChatSidebarBtn').onclick = () => { startNewChat(); sidebar.classList.remove('open'); overlay.style.display='none'; };

        function generateId() { return Date.now().toString(36) + Math.random().toString(36).substr(2); }
        async function loadChats() {
            const q = query(collection(db, `users/${currentUser.uid}/chats`), orderBy('updatedAt', 'desc'));
            const snap = await getDocs(q); chatList.innerHTML = '';
            snap.forEach(doc => {
                const data = doc.data(); const div = document.createElement('div');
                div.className = `chat-item ${currentChatId === doc.id ? 'active' : ''}`;
                div.innerHTML = `<span class="truncate text-sm flex-1">${data.title || 'Yeni Sohbet'}</span><i class="fas fa-trash opacity-50 hover:opacity-100 hover:text-red-500 p-1" onclick="event.stopPropagation(); deleteChat('${doc.id}')"></i>`;
                div.onclick = () => { loadSpecificChat(doc.id); sidebar.classList.remove('open'); overlay.style.display='none'; };
                chatList.appendChild(div);
            });
        }
        async function startNewChat() {
            currentChatId = generateId(); currentMessages = [];
            chatContainer.innerHTML = '<div class="msg msg-ai glass"><b>Legends AI:</b> Sistem hazır. Kurulum ve kodlama için emrindeyim.</div>';
            await setDoc(doc(db, `users/${currentUser.uid}/chats`, currentChatId), { title: "Yeni Sohbet", updatedAt: serverTimestamp(), messages: [] }); loadChats();
        }
        async function loadSpecificChat(chatId) {
            currentChatId = chatId; chatContainer.innerHTML = '';
            const docSnap = await getDoc(doc(db, `users/${currentUser.uid}/chats`, chatId));
            if (docSnap.exists()) { currentMessages = docSnap.data().messages || []; currentMessages.forEach(m => addChatUI(m.content, m.role)); } loadChats();
        }
        window.deleteChat = async function(chatId) { if(confirm("Sohbet silinsin mi?")) { await deleteDoc(doc(db, `users/${currentUser.uid}/chats`, chatId)); if(currentChatId === chatId) startNewChat(); else loadChats(); } }

        // MESAJ GÖNDERME VE YAN YANA BUTONLAR
        document.getElementById('sendBtn').onclick = sendMsg;
        userInput.addEventListener('keypress', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMsg(); } });
        async function sendMsg() {
            const val = userInput.value.trim(); if(!val) return;
            userInput.value = ""; userInput.style.height = 'auto'; actionMenu.classList.remove('show');
            addChatUI(val, 'user'); const loadId = 'ai-' + Date.now(); addLoadingUI(loadId);
            currentMessages.push({role: "user", content: val});
            await updateDoc(doc(db, `users/${currentUser.uid}/chats`, currentChatId), { title: currentMessages[0].content.substring(0, 25), messages: currentMessages, updatedAt: serverTimestamp() });
            
            try {
                const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ messages: currentMessages, temperature: currentTemperature }) });
                const data = await res.json();
                document.getElementById(loadId).remove(); addChatUI(data.answer, 'assistant');
                currentMessages.push({role: "assistant", content: data.answer});
                await updateDoc(doc(db, `users/${currentUser.uid}/chats`, currentChatId), { messages: currentMessages, updatedAt: serverTimestamp() });
            } catch(e) { document.getElementById(loadId).innerText = "❌ Sunucu hatası!"; }
        }
        
        function addChatUI(text, role) {
            const d = document.createElement('div');
            d.className = `msg msg-${role === 'user' ? 'user' : 'ai'} glass`;
            d.innerHTML = role === 'user' ? text : marked.parse(text);
            chatContainer.appendChild(d);
            
            if (role === 'assistant') {
                d.querySelectorAll('pre').forEach(pre => {
                    const codeText = pre.innerText; 
                    const actionDiv = document.createElement('div'); 
                    actionDiv.className = 'code-actions';
                    
                    // 1. GÜNCELLE BUTONU (EN SOLDA)
                    const updateBtn = document.createElement('button'); updateBtn.className = 'code-btn btn-update'; updateBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Güncelle';
                    updateBtn.onclick = () => {
                        userInput.value = "Lütfen aşağıdaki kodun HİÇBİR özelliğini SİLMEDEN üstüne şu güncellemeyi yap: [...]\n\nİşte mevcut kod:\n```\n" + codeText + "\n```";
                        userInput.style.height = '100px'; userInput.focus(); userInput.setSelectionRange(75, 78);
                    };
                    actionDiv.appendChild(updateBtn);

                    // 2. KOPYALA BUTONU (ORTADA)
                    const copyBtn = document.createElement('button'); copyBtn.className = 'code-btn'; copyBtn.innerHTML = '<i class="fas fa-copy"></i> Kopyala';
                    copyBtn.onclick = () => { navigator.clipboard.writeText(codeText); copyBtn.innerHTML = '<i class="fas fa-check text-green-400"></i> Alındı'; setTimeout(() => copyBtn.innerHTML = '<i class="fas fa-copy"></i> Kopyala', 2000); };
                    actionDiv.appendChild(copyBtn);

                    // 3. ÖNİZLE BUTONU (SAĞDA, EĞER HTML İSE)
                    if(codeText.includes('<html') || codeText.includes('<body') || codeText.includes('document.createElement')) {
                        const previewBtn = document.createElement('button'); previewBtn.className = 'code-btn btn-preview'; previewBtn.innerHTML = '<i class="fas fa-play"></i> Önizle'; previewBtn.onclick = () => window.openPreview(codeText); actionDiv.appendChild(previewBtn);
                    }
                    pre.appendChild(actionDiv);
                });
            }
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        function addLoadingUI(id) {
            const d = document.createElement('div'); d.className = `msg msg-ai glass p-4 text-orange-500 font-bold`; d.id = id;
            d.innerHTML = `<i class="fas fa-circle-notch fa-spin"></i> İşleniyor...`;
            chatContainer.appendChild(d); chatContainer.scrollTop = chatContainer.scrollHeight;
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
    incoming_messages = data.get('messages', [])
    temperature = data.get('temperature', 0.2)
    
    system_msg = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages_for_llm = system_msg + incoming_messages
    success = False; answer = "Hata"
    while current_key_index < len(API_KEYS):
        try:
            client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=API_KEYS[current_key_index])
            res = client.chat.completions.create(model=MODEL, messages=messages_for_llm, temperature=temperature)
            answer = res.choices[0].message.content; success = True; break
        except: current_key_index += 1
    if not success: answer = "❌ Limit doldu!"
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
