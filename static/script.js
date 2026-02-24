cat << 'EOF' > static/script.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut, signInWithEmailAndPassword, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
import { getFirestore, collection, doc, setDoc, getDoc, deleteDoc, query, orderBy, onSnapshot, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

// FIREBASE YAPILANDIRMASI
const app = initializeApp({ apiKey: "AIzaSyAnNzL2wSLEsy6DprleCNSq9elnv3X7BTg", authDomain: "legendsai-3e2d6.firebaseapp.com", projectId: "legendsai-3e2d6" });
const auth = getAuth(app); const db = getFirestore(app);
let cUser = null, cChatId = null, history = [], config = { temperature: 0.3, systemPrompt: "" };

// YARDIMCI FONKSİYONLAR (Toast, Base64)
const toast = (m, t='info') => Toastify({text: m, duration: 3000, style: {background: t==='error'?"#ef4444":"#3b82f6", borderRadius: "12px", fontSize: "13px", fontWeight: "600", boxShadow: "0 10px 30px rgba(0,0,0,0.3)"}}).showToast();
function getRaw(b64) { return decodeURIComponent(escape(atob(b64))); }

// MARKDOWN RENDERER (Kod Blokları ve Butonlar)
const renderer = new marked.Renderer();
renderer.code = function(code, lang) {
    const raw = typeof code === 'object' ? code.text : String(code);
    const b64 = btoa(unescape(encodeURIComponent(raw))); // Kusursuz şifreleme
    const isH = (lang === 'html' || raw.includes('<!doctype') || raw.includes('<html'));
    // MOBİL UYUMLU İKONLU BUTONLAR
    return `<pre><code class="language-${lang}">${raw.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>
    <div class="code-toolbar">
        <button onclick="window.uC('${b64}')" class="code-btn btn-v2"><i class="fas fa-level-up-alt"></i> v2 Geliştir</button>
        <button onclick="window.cC('${b64}', this)" class="code-btn"><i class="fas fa-copy"></i> Kopyala</button>
        <button onclick="window.dwn('${b64}')" class="code-btn btn-dl"><i class="fas fa-download"></i> İndir</button>
        ${isH ? `<button onclick="window.pC('${b64}')" class="code-btn btn-pre"><i class="fas fa-play"></i> CANLI İZLE</button>` : ''}
    </div>`;
};
marked.setOptions({ renderer: renderer, breaks: true });

// BUTON AKSİYONLARI (Global Window Fonksiyonları)
window.uC = (b) => { document.getElementById('userInput').value = `Bu kodu bozmadan, profesyonelce geliştir ve v2 sürümünü yap:\\n\\n\`\`\`\\n${getRaw(b)}\`\`\``; document.getElementById('userInput').focus(); };
window.cC = (b, btn) => { navigator.clipboard.writeText(getRaw(b)); btn.innerHTML = '<i class="fas fa-check"></i> Kopyalandı'; setTimeout(()=>btn.innerHTML='<i class="fas fa-copy"></i> Kopyala', 2000); toast('Kod panoya alındı.'); };
window.pC = (b) => { document.getElementById('previewModal').classList.add('active'); document.getElementById('pFrame').srcdoc = getRaw(b); };
window.dwn = (b) => { const blob = new Blob([getRaw(b)], {type: "text/html;charset=utf-8"}); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = "Legends_Project.html"; document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url); toast('Dosya indirildi.'); };
window.dC = async (id) => { if(confirm('Bu proje kalıcı olarak silinsin mi?')) { await deleteDoc(doc(db, `users/${cUser.uid}/chats`, id)); startN(); toast('Proje silindi.', 'error'); }};

// AUTH VE SİSTEM BAŞLANGICI
onAuthStateChanged(auth, async (u) => {
    if(u){ cUser = u; document.getElementById('auth-screen').style.display = 'none'; document.getElementById('uName').innerText = u.email.split('@')[0].toUpperCase(); document.querySelector('.avatar').innerText = u.email[0].toUpperCase();
        const d = await getDoc(doc(db, `users/${u.uid}/settings`, 'cfg')); if(d.exists()){ config = d.data(); document.getElementById('tRange').value = config.temperature; document.getElementById('sysPrompt').value = config.systemPrompt || ""; }
        onSnapshot(query(collection(db, `users/${u.uid}/chats`), orderBy('updatedAt', 'desc')), (s) => {
            const l = document.getElementById('historyList'); l.innerHTML = "";
            s.forEach(d => { const div = document.createElement('div'); div.className = `sidebar-item ${cChatId===d.id ? 'active' : ''}`; div.innerHTML = `<span class="truncate">${d.data().title}</span><i class="fas fa-trash" onclick="event.stopPropagation(); window.dC('${d.id}')"></i>`; div.onclick = () => { loadC(d.id); if(window.innerWidth<768) document.getElementById('sidebar').classList.remove('open'); }; l.appendChild(div); });
        }); startN(); toast(`Hoş geldin, ${u.email.split('@')[0]}!`);
    } else { document.getElementById('auth-screen').style.display = 'flex'; }
});

// OLAY DİNLEYİCİLERİ (Event Listeners)
document.getElementById('btnLogin').onclick = () => signInWithEmailAndPassword(auth, document.getElementById('authEmail').value, document.getElementById('authPass').value).catch(e => toast(e.message, 'error'));
document.getElementById('btnRegister').onclick = () => createUserWithEmailAndPassword(auth, document.getElementById('authEmail').value, document.getElementById('authPass').value).then(() => toast('Kayıt başarılı!')).catch(e => toast(e.message, 'error'));
document.getElementById('btnGoogle').onclick = () => signInWithPopup(auth, new GoogleAuthProvider()).catch(e => toast(e.message, 'error'));
document.getElementById('btnLogout').onclick = () => { signOut(auth); document.getElementById('settingsModal').classList.remove('active'); };
document.getElementById('saveSet').onclick = async () => { config.systemPrompt = document.getElementById('sysPrompt').value; config.temperature = parseFloat(document.getElementById('tRange').value); await setDoc(doc(db, `users/${cUser.uid}/settings`, 'cfg'), config); toast('Ayarlar kaydedildi.'); document.getElementById('settingsModal').classList.remove('active'); };
document.getElementById('sendBtn').onclick = sM;
document.getElementById('userInput').oninput = function(){ this.style.height = 'auto'; this.style.height = this.scrollHeight + 'px'; };
document.getElementById('userInput').onkeydown = (e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sM(); } };

// SOHBET FONKSİYONLARI
async function startN() { cChatId = "chat_"+Date.now(); history = []; document.getElementById('chat-container').innerHTML = '<div class="h-full flex flex-col items-center justify-center opacity-10 select-none pointer-events-none"><i class="fas fa-cube text-8xl mb-6 text-white"></i><p class="font-black tracking-[0.5em] text-sm text-white uppercase">V31.0 FOUNDATION</p></div>'; await setDoc(doc(db, `users/${cUser.uid}/chats`, cChatId), { title: "Yeni Proje", updatedAt: serverTimestamp(), messages: [] }); if(window.innerWidth<768) document.getElementById('sidebar').classList.remove('open'); }
async function loadC(id) { cChatId = id; const d = await getDoc(doc(db, `users/${cUser.uid}/chats`, id)); if(d.exists()){ history = d.data().messages || []; rC(); } }
async function sM() {
    const v = document.getElementById('userInput').value.trim(); if(!v) return;
    document.getElementById('userInput').value = ""; document.getElementById('userInput').style.height = 'auto'; addUI(v, 'user'); history.push({role: "user", content: v});
    const d = document.createElement('div'); d.className = 'msg-ai'; d.innerHTML = `<div class="ai-avatar-box"><i class="fas fa-cube"></i></div><div class="markdown-body typing"></div>`;
    document.getElementById('chat-container').appendChild(d); document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
    let full = ""; const cDiv = d.querySelector('.markdown-body');
    try {
        const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ messages: history, settings: config }) });
        const r = res.body.getReader(); const dec = new TextDecoder();
        while (true) { const { done, value } = await r.read(); if (done) break; full += dec.decode(value, {stream: true}); cDiv.innerHTML = marked.parse(full); document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight; }
        cDiv.classList.remove('typing'); history.push({role: "assistant", content: full}); await updateDoc(doc(db, `users/${cUser.uid}/chats`, cChatId), { title: history[0].content.substring(0,25), messages: history, updatedAt: serverTimestamp() });
    } catch(e) { cDiv.innerHTML = "Bağlantı hatası patron."; cDiv.classList.remove('typing'); toast('Sinyal zayıf.', 'error'); }
}
function addUI(t, r) { const d = document.createElement('div'); d.className = r==='user'?'msg-user':'msg-ai'; if(r==='user') d.innerText=t; else d.innerHTML=`<div class="ai-avatar-box"><i class="fas fa-cube"></i></div><div class="markdown-body">${marked.parse(t)}</div>`; document.getElementById('chat-container').appendChild(d); document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight; }
function rC() { document.getElementById('chat-container').innerHTML = ""; history.forEach(m => addUI(m.content, m.role)); }

// UI ETKİLEŞİMLERİ
document.getElementById('openSidebar').onclick = () => document.getElementById('sidebar').classList.add('open');
document.getElementById('closeSidebar').onclick = () => document.getElementById('sidebar').classList.remove('open');
document.getElementById('openSettings').onclick = () => document.getElementById('settingsModal').classList.add('active');
document.getElementById('closeSettings').onclick = () => document.getElementById('settingsModal').classList.remove('active');
document.getElementById('closePreview').onclick = () => document.getElementById('previewModal').classList.remove('active');
document.getElementById('tRange').oninput = (e) => { document.getElementById('tVal').innerText = e.target.value; };
EOF

