from flask import Flask, render_template_string, request, jsonify
import requests, json, os
from openai import OpenAI

app = Flask(__name__)

# --- LEGENDS AI V11.4 CORE (GÜNCELLE BUTONU VE KURULUM REHBERİ) ---
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

# YENİ SİSTEM KOMUTU: AI'A NASIL KURULACAĞINI ANLATMASINI EMRETTİK
SYSTEM_PROMPT = "Sen Legends AI'sın. Şenol'un baş yazılım mimarısın. 1) Sadece kod yaz. 2) Asla yarıda kesme. 3) Tek HTML dosyasında kusursuz iş çıkar. 4) Yazdığın kodların en altına, bu kodun nasıl kurulacağını ve çalıştırılacağını (adım adım) kısaca açıkla."

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Legends AI | Pro",
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
    <title>LEGENDS AI | PRO</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
    <link rel="manifest" href="/manifest.json">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root { --primary: #f97316; --bg: #020617; --card: rgba(15, 23, 42, 0.85); }
        body { background: var(--bg); color: #f1f5f9; font-family: 'Inter', sans-serif; height: 100dvh; overflow: hidden; margin: 0; display: flex; flex-direction: column; }
        .glass { background: var(--card); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.08); }
        
        #auth-screen { position: absolute; inset: 0; z-index: 200; display: flex; flex-direction: column; justify-content: center; align-items: center; background: var(--bg); padding: 20px; }
        .auth-box { width: 100%; max-width: 350px; padding: 30px; border-radius: 30px; display: flex; flex-direction: column; gap: 15px; }
        .auth-input { width: 100%; padding: 14px; border-radius: 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; outline: none; }
        .auth-btn { width: 100%; padding: 14px; border-radius: 12px; font-weight: bold; background: var(--primary); color: white; cursor: pointer; transition: 0.2s; }
        .auth-btn:active { transform: scale(0.98); }
        .google-btn { background: white; color: black; display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 10px; }
        
        #sidebar { position: absolute; left: -300px; top: 0; bottom: 0; width: 280px; z-index: 150; transition: 0.3s; display: flex; flex-direction: column; }
        #sidebar.open { left: 0; }
        .chat-item { padding: 12px 15px; border-radius: 10px; margin-bottom: 8px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); }
        .chat-item:hover, .chat-item.active { background: rgba(249, 115, 22, 0.2); border-left: 3px solid var(--primary); }
        
        header { padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; z-index: 50; border-bottom: 1px solid rgba(255,255,255,0.05); }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; scroll-behavior: smooth; }
        .msg { max-width: 92%; padding: 16px 20px; border-radius: 24px; line-height: 1.6; font-size: 15px; animation: slideIn 0.3s ease; }
        .msg-user { align-self: flex-end; background: var(--primary); color: white; border-bottom-right-radius: 4px; }
        .msg-ai { align-self: flex-start; background: rgba(30, 41, 59, 0.7); border-bottom-left-radius: 4px; width: 100%; }
        
        .input-area { padding: 16px; padding-bottom: max(16px, env(safe-area-inset-bottom)); position: relative; }
        .input-box { border-radius: 28px; padding: 8px 8px 8px 12px; display: flex; align-items: flex-end; gap: 10px; }
        .attach-btn { padding: 10px; color: #94a3b8; cursor: pointer; font-size: 20px; transition: 0.2s; }
        .attach-btn:hover { color: var(--primary); }
        textarea { flex: 1; background: transparent; border: none; outline: none; color: white; max-height: 140px; resize: none; font-size: 16px; padding: 10px 0; }
        .circle-btn { width: 44px; height: 44px; border-radius: 50%; display: flex; justify-content: center; align-items: center; cursor: pointer; background: var(--primary); color: white; flex-shrink: 0; }
        
        #actionMenu { display: none; position: absolute; bottom: 80px; left: 20px; flex-direction: column; gap: 5px; padding: 10px; border-radius: 16px; min-width: 170px; z-index: 100; }
        #actionMenu.show { display: flex; animation: slideUp 0.2s ease; }
        .action-item { display: flex; align-items: center; gap: 10px; padding: 12px; color: white; cursor: pointer; border-radius: 10px; font-size: 14px; transition: 0.2s; }
        .action-item:hover { background: rgba(249, 115, 22, 0.2); color: var(--primary); }

        pre { background: #000 !important; border-radius: 16px; padding: 45px 14px 14px 14px; margin: 15px 0; border: 1px solid rgba(255,255,255,0.1); position: relative; max-width: 100%; overflow-x: auto; }
        code { font-family: 'Fira Code', monospace; font-size: 13px; white-space: pre; }
        .code-actions { position: absolute; top: 10px; right: 10px; display: flex; gap: 8px; z-index: 10; }
        .code-btn { background: rgba(255,255,255,0.15); border:none; color: white; padding: 6px 12px; border-radius: 8px; font-size: 11px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 5px; backdrop-filter: blur(5px); transition: 0.2s; }
        .code-btn:hover { background: var(--primary); }
        
        /* GÜNCELLE BUTONU ÖZEL RENK */
        .btn-update { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
        .btn-update:hover { background: #3b82f6; color: white; }

        .modal-container { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 300; justify-content: center; align-items: center; padding: 20px; }
        .modal-container.show { display: flex; animation: fadeIn 0.2s ease; }
        .modal-box { width: 100%; max-width: 500px; max-height: 90vh; display: flex; flex-direction: column; border-radius: 24px; overflow: hidden; }
        .modal-header { padding: 16px 20px; background: rgba(0,0,0,0.5); display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .modal-close { text-white; font-size: 24px; cursor: pointer; opacity: 0.7; transition: 0.2s; }
        .modal-close:hover { opacity: 1; color: red; }

        #previewFrame { flex: 1; width: 100%; background: #fff; border: none; min-height: 400px; }

        .settings-content { padding: 24px; display: flex; flex-direction: column; gap: 20px; }
        .setting-item label { display: block; font-size: 13px; color: #94a3b8; margin-bottom: 8px; font-weight: bold; }
        .setting-input { width: 100%; padding: 12px; border-radius: 10px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; outline: none; }
        input[type=range] { width: 100%; accent-color: var(--primary); }

        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        #overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.5); z-index: 140; display: none; }
    </style>
</head>
<body>

    <div id="auth-screen">
        <div class="text-center mb-8"><i class="fas fa-crown text-5xl text-orange-500 mb-4 drop-shadow-[0_0_15px_rgba(249,115,22,0.5)]"></i><h1 class="text-3xl font-black">LEGENDS AI</h1><p class="text-gray-400 text-sm mt-2">Pro Sürüm Girişi</p></div>
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
            <button id="menuBtn" class="text-xl text-white p-2"><i class="fas fa-bars"></i></button>
            <div class="font-black text-lg flex items-center gap-2"><i class="fas fa-crown text-orange-500"></i> LEGENDS PRO</div>
            <button id="newChatTopBtn" class="text-orange-500 text-xl p-2"><i class="fas fa-plus-circle"></i></button>
        </header>
        
        <div id="chat-container"></div>
        
        <div class="input-area">
            <div id="actionMenu" class="glass">
                <div class="action-item" onclick="alert('Fotoğraf analizi yakında eklenecek!')"><i class="fas fa-camera w-6 text-orange-500"></i> Fotoğraf Çek</div>
                <div class="action-item" onclick="alert('Dosya okuma yakında eklenecek!')"><i class="fas fa-file-upload w-6 text-blue-500"></i> Dosya Yükle</div>
                <div class="action-item" id="openSettingsBtn"><i class="fas fa-sliders-h w-6 text-gray-400"></i> Ayarlar</div>
            </div>

            <div class="input-box glass">
                <div id="attachBtn" class="attach-btn"><i class="fas fa-plus"></i></div>
                <textarea id="userInput" placeholder="Bir şeyler yazın..." rows="1" oninput="this.style.height='auto';this.style.height=this.scrollHeight+'px'"></textarea>
                <div id="sendBtn" class="circle-btn"><i class="fas fa-paper-plane"></i></div>
            </div>
        </div>
    </div>

    <div id="overlay"></div>
    <aside id="sidebar" class="glass border-r border-white/5 p-4">
        <div class="flex items-center gap-3 mb-6 p-2 bg-white/5 rounded-xl">
            <div class="w-10 h-10 rounded-full bg-orange-500 flex items-center justify-center font-bold text-lg" id="userAvatar">A</div>
            <div class="flex-1 overflow-hidden"><div class="text-sm font-bold truncate" id="userName">Kullanıcı</div><div class="text-[10px] text-green-400 flex items-center gap-1"><i class="fas fa-circle text-[8px]"></i> Çevrimiçi</div></div>
        </div>
        <button id="newChatSidebarBtn" class="w-full py-3 bg-orange-500 text-white rounded-xl font-bold mb-4 flex items-center justify-center gap-2 hover:bg-orange-600 transition"><i class="fas fa-plus"></i> YENİ SOHBET</button>
        <div class="text-[10px] text-gray-500 font-bold mb-2 px-2 uppercase">Geçmiş</div>
        <div id="chatHistoryList" class="flex-1 overflow-y-auto px-2"></div>
        <button id="btnLogout" class="mt-4 p-3 bg-red-500/10 text-red-500 rounded-xl text-sm font-bold w-full hover:bg-red-500/20 transition"><i class="fas fa-sign-out-alt"></i> ÇIKIŞ</button>
    </aside>

    <div id="previewModal" class="modal-container">
        <div class="modal-box glass h-full">
            <div class="modal-header">
                <div class="font-bold text-orange-500 flex items-center gap-2"><i class="fas fa-play-circle"></i> Canlı Önizleme</div>
                <i class="fas fa-times modal-close" id="closePreviewBtn"></i>
            </div>
            <iframe id="previewFrame"></iframe>
        </div>
    </div>

    <div id="settingsModal" class="modal-container">
        <div class="modal-box glass">
            <div class="modal-header">
                <div class="font-bold text-white flex items-center gap-2"><i class="fas fa-cog text-gray-400"></i> Uygulama Ayarları</div>
                <i class="fas fa-times modal-close" id="closeSettingsBtn"></i>
            </div>
            <div class="settings-content">
                <div class="setting-item">
                    <label>Yapay Zeka Modeli (Motor)</label>
                    <select class="setting-input" disabled><option>Llama 3.3 70B (V10 Motor - Aktif)</option></select>
                </div>
                 <div class="setting-item">
                    <label class="flex justify-between"><span>Yaratıcılık Seviyesi (Temperature)</span> <span id="tempValue" class="text-orange-500">0.2</span></label>
                    <input type="range" id="tempRange" min="0" max="1" step="0.1" value="0.2">
                    <div class="flex justify-between text-xs text-gray-500 mt-1"><span>Mantıklı</span><span>Dengeli</span><span>Yaratıcı</span></div>
                </div>
                <button id="saveSettingsBtn" class="auth-btn mt-2"><i class="fas fa-save"></i> AYARLARI GÜNCELLE</button>
            </div>
        </div>
    </div>

    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
        import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, GoogleAuthProvider, signInWithRedirect, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
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

        let currentUser = null; let currentChatId = null; let currentMessages = []; let currentTemperature = 0.2;

        const authScreen = document.getElementById('auth-screen'); const appScreen = document.getElementById('app-screen');
        const sidebar = document.getElementById('sidebar'); const overlay = document.getElementById('overlay');
        const chatContainer = document.getElementById('chat-container'); const chatList = document.getElementById('chatHistoryList');
        const userInput = document.getElementById('userInput'); const actionMenu = document.getElementById('actionMenu');
        const previewModal = document.getElementById('previewModal'); const settingsModal = document.getElementById('settingsModal');
        const tempRange = document.getElementById('tempRange'); const tempValue = document.getElementById('tempValue');

        document.getElementById('attachBtn').onclick = () => { actionMenu.classList.toggle('show'); };
        
        window.openPreview = function(code) { previewModal.classList.add('show'); document.getElementById('previewFrame').srcdoc = code; };
        document.getElementById('closePreviewBtn').onclick = () => { previewModal.classList.remove('show'); document.getElementById('previewFrame').srcdoc = ""; };
        
        document.getElementById('openSettingsBtn').onclick = () => { actionMenu.classList.remove('show'); settingsModal.classList.add('show'); };
        document.getElementById('closeSettingsBtn').onclick = () => { settingsModal.classList.remove('show'); };
        
        tempRange.oninput = () => { tempValue.innerText = tempRange.value; };
        document.getElementById('saveSettingsBtn').onclick = () => {
            currentTemperature = parseFloat(tempRange.value); settingsModal.classList.remove('show');
            const toast = document.createElement('div'); toast.className = 'fixed bottom-20 left-1/2 -translate-x-1/2 bg-orange-500 text-white px-4 py-2 rounded-full text-sm font-bold shadow-lg z-50';
            toast.innerHTML = '<i class="fas fa-check-circle"></i> Ayarlar Güncellendi!'; document.body.appendChild(toast); setTimeout(() => toast.remove(), 2000);
        };

onAuthStateChanged(auth, (user) => {
            if (user) {
                currentUser = user;
                document.getElementById('userName').innerText = user.displayName || user.email.split('@')[0];
                document.getElementById('userAvatar').innerText = (user.displayName || user.email)[0].toUpperCase();
                authScreen.style.display = 'none'; appScreen.classList.remove('hidden'); loadChats(); startNewChat();
            } else { currentUser = null; authScreen.style.display = 'flex'; appScreen.classList.add('hidden'); }
        });

        document.getElementById('btnLogin').onclick = () => { const e=document.getElementById('email').value,p=document.getElementById('password').value; signInWithEmailAndPassword(auth,e,p).catch(err=>alert(err.message)); };
        document.getElementById('btnRegister').onclick = () => { const e=document.getElementById('email').value,p=document.getElementById('password').value; createUserWithEmailAndPassword(auth,e,p).catch(err=>alert(err.message)); };
        document.getElementById('btnGoogle').onclick = () => { signInWithRedirect(auth, new GoogleAuthProvider()).catch(err=>alert(err.message)); };
        document.getElementById('btnLogout').onclick = () => { signOut(auth); sidebar.classList.remove('open'); overlay.style.display='none'; };

        document.getElementById('menuBtn').onclick = () => { sidebar.classList.add('open'); overlay.style.display='block'; actionMenu.classList.remove('show'); };
        overlay.onclick = () => { sidebar.classList.remove('open'); overlay.style.display='none'; actionMenu.classList.remove('show'); };
        document.getElementById('newChatTopBtn').onclick = startNewChat;
        document.getElementById('newChatSidebarBtn').onclick = () => { startNewChat(); sidebar.classList.remove('open'); overlay.style.display='none'; };

        function generateId() { return Date.now().toString(36) + Math.random().toString(36).substr(2); }
        async function loadChats() {
            chatList.innerHTML = '<div class="text-center text-xs text-gray-500 mt-4">Yükleniyor...</div>';
            const q = query(collection(db, `users/${currentUser.uid}/chats`), orderBy('updatedAt', 'desc'));
            const snap = await getDocs(q); chatList.innerHTML = '';
            snap.forEach(doc => {
                const data = doc.data(); const div = document.createElement('div');
                div.className = `chat-item ${currentChatId === doc.id ? 'active' : ''}`;
                div.innerHTML = `<span class="truncate text-sm flex-1">${data.title || 'Yeni Sohbet'}</span><i class="fas fa-trash text-gray-500 hover:text-red-500 ml-2 p-1" onclick="event.stopPropagation(); deleteChat('${doc.id}')"></i>`;
                div.onclick = () => { loadSpecificChat(doc.id); sidebar.classList.remove('open'); overlay.style.display='none'; };
                chatList.appendChild(div);
            });
        }
        async function startNewChat() {
            currentChatId = generateId(); currentMessages = [];
            chatContainer.innerHTML = '<div class="msg msg-ai glass flex items-center gap-2"><i class="fas fa-robot text-orange-500"></i> <b>Legends AI:</b> Sistem hazır. Kurulum ve kodlama için emrindeyim.</div>';
            await setDoc(doc(db, `users/${currentUser.uid}/chats`, currentChatId), { title: "Yeni Sohbet", updatedAt: serverTimestamp(), messages: [] }); loadChats();
        }
        async function loadSpecificChat(chatId) {
            currentChatId = chatId; chatContainer.innerHTML = '';
            const docSnap = await getDoc(doc(db, `users/${currentUser.uid}/chats`, chatId));
            if (docSnap.exists()) { currentMessages = docSnap.data().messages || []; currentMessages.forEach(m => addChatUI(m.content, m.role)); } loadChats();
        }
        window.deleteChat = async function(chatId) { if(confirm("Sohbet silinsin mi?")) { await deleteDoc(doc(db, `users/${currentUser.uid}/chats`, chatId)); if(currentChatId === chatId) startNewChat(); else loadChats(); } }

        document.getElementById('sendBtn').onclick = sendMsg;
        userInput.addEventListener('keypress', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMsg(); } });
        async function sendMsg() {
            const val = userInput.value.trim(); if(!val) return;
            userInput.value = ""; userInput.style.height = 'auto'; actionMenu.classList.remove('show');
            addChatUI(val, 'user');
            const loadId = 'ai-' + Date.now(); addLoadingUI(loadId);
            currentMessages.push({role: "user", content: val});
            await updateDoc(doc(db, `users/${currentUser.uid}/chats`, currentChatId), { title: currentMessages[0].content.substring(0, 25), messages: currentMessages, updatedAt: serverTimestamp() });
            loadChats(); 
            try {
                const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ messages: currentMessages, temperature: currentTemperature }) });
                const data = await res.json();
                document.getElementById(loadId).remove();
                addChatUI(data.answer, 'assistant');
                currentMessages.push({role: "assistant", content: data.answer});
                await updateDoc(doc(db, `users/${currentUser.uid}/chats`, currentChatId), { messages: currentMessages, updatedAt: serverTimestamp() });
            } catch(e) { document.getElementById(loadId).innerText = "❌ Sunucu hatası!"; }
        }
        
        function addChatUI(text, role) {
            const d = document.createElement('div');
            d.className = `msg msg-${role === 'user' ? 'user' : 'ai'} glass relative group`;
            d.innerHTML = role === 'user' ? text : marked.parse(text);
            chatContainer.appendChild(d);
            if (role === 'assistant') {
                d.querySelectorAll('pre').forEach(pre => {
                    const codeText = pre.innerText; const actionDiv = document.createElement('div'); actionDiv.className = 'code-actions';
                    
                    // KOPYALA BUTONU
                    const copyBtn = document.createElement('button'); copyBtn.className = 'code-btn'; copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                    copyBtn.onclick = () => { navigator.clipboard.writeText(codeText); copyBtn.innerHTML = '<i class="fas fa-check text-green-400"></i>'; setTimeout(() => copyBtn.innerHTML = '<i class="fas fa-copy"></i>', 2000); };
                    actionDiv.appendChild(copyBtn);
                    
                    // YENİ: GÜNCELLE BUTONU (UPREAD)
                    const updateBtn = document.createElement('button'); updateBtn.className = 'code-btn btn-update'; updateBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
                    updateBtn.onclick = () => {
                        const box = document.getElementById('userInput');
                        box.value = "Lütfen aşağıdaki kodun HİÇBİR özelliğini SİLMEDEN ve BOZMADAN üstüne şu güncellemeyi yap:\n\n[İSTEDİĞİN YENİ ÖZELLİĞİ BURAYA YAZ]\n\nİşte mevcut kod:\n```\n" + codeText + "\n```";
                        box.style.height = 'auto'; box.style.height = Math.min(box.scrollHeight, 150) + 'px';
                        box.focus(); box.setSelectionRange(84, 118); // Yazı yazılacak yeri seçili hale getir
                    };
                    actionDiv.appendChild(updateBtn);

                    // ÖNİZLE BUTONU
                    if(codeText.includes('<html') || codeText.includes('<body') || codeText.includes('document.createElement')) {
                        const previewBtn = document.createElement('button'); previewBtn.className = 'code-btn bg-orange-500/20 text-orange-500 hover:bg-orange-500 hover:text-white'; previewBtn.innerHTML = '<i class="fas fa-play"></i>'; previewBtn.onclick = () => window.openPreview(codeText); actionDiv.appendChild(previewBtn);
                    }
                    pre.appendChild(actionDiv);
                });
            }
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        function addLoadingUI(id) {
            const d = document.createElement('div'); d.className = `msg msg-ai glass flex items-center gap-2`; d.id = id;
            d.innerHTML = `<i class="fas fa-circle-notch fa-spin text-orange-500"></i> <span class="opacity-75">Düşünüyor...</span>`;
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
