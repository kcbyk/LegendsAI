from flask import Flask, render_template_string, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# --- LEGENDS AI V19.0 (VERCEL CLONE EDITION) ---
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
    return jsonify({"answer": "❌ Tüm anahtarların limiti doldu!"})

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
    <meta charset="UTF-8">
    <title>Legends Master Pro</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>tailwind.config = { darkMode: 'class', theme: { extend: { colors: { vercelBg: '#000000', vercelBorder: '#333333', vercelHover: '#1A1A1A' } } } }</script>
    <style>
        body { background: #000; color: #ededed; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; height: 100dvh; display: flex; }
        .sidebar { width: 260px; background: #000; border-right: 1px solid var(--vercelBorder); transition: transform 0.3s; }
        .msg-user { background: #1A1A1A; border: 1px solid var(--vercelBorder); border-radius: 12px; padding: 16px; margin-left: auto; max-width: 80%; }
        .msg-ai { padding: 16px 0; max-width: 100%; border-bottom: 1px solid var(--vercelBorder); }
        pre { background: #0A0A0A !important; border: 1px solid var(--vercelBorder); border-radius: 8px; padding: 40px 16px 16px 16px; margin: 16px 0; position: relative; overflow-x: auto; }
        .code-actions { position: absolute; top: 8px; right: 8px; display: flex; gap: 8px; }
        .code-btn { padding: 4px 8px; border-radius: 6px; font-size: 12px; color: #888; background: transparent; border: 1px solid var(--vercelBorder); cursor: pointer; transition: 0.2s; }
        .code-btn:hover { background: #1A1A1A; color: #fff; }
        .input-container { background: #000; border: 1px solid var(--vercelBorder); border-radius: 12px; padding: 8px 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        textarea:focus { outline: none; }
        @media (max-width: 768px) { .sidebar { position: absolute; transform: translateX(-100%); z-index: 50; height: 100%; } .sidebar.open { transform: translateX(0); } }
    </style>
</head>
<body>

    <aside id="sidebar" class="sidebar flex flex-col">
        <div class="p-4 flex items-center justify-between border-b border-[#333]">
            <span class="font-bold tracking-tight">LEGENDS PRO</span>
            <button id="closeSidebar" class="md:hidden text-gray-400"><i class="fas fa-times"></i></button>
        </div>
        <div class="p-3">
            <button id="newChatBtn" class="w-full text-left p-3 rounded-lg hover:bg-vercelHover border border-[#333] flex items-center gap-2 text-sm transition">
                <i class="fas fa-plus text-xs"></i> New Chat
            </button>
        </div>
        <div id="historyList" class="flex-1 overflow-y-auto p-3 space-y-1 text-sm text-gray-400">
            </div>
        <div class="p-4 border-t border-[#333] flex items-center justify-between text-sm">
            <div class="flex items-center gap-2"><div class="w-8 h-8 rounded-full bg-white text-black flex items-center justify-center font-bold">ŞK</div> Şenol Kocabıyık</div>
            <button class="text-gray-500 hover:text-white"><i class="fas fa-cog"></i></button>
        </div>
    </aside>

    <main class="flex-1 flex flex-col relative overflow-hidden">
        <header class="h-14 flex items-center px-4 border-b border-[#333] md:hidden">
            <button id="openSidebar" class="text-gray-400 mr-3"><i class="fas fa-bars"></i></button>
            <span class="font-bold">LEGENDS PRO</span>
        </header>

        <div id="chat-container" class="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 pb-32">
            <div class="flex flex-col items-center justify-center h-full text-center text-gray-500">
                <i class="fas fa-cube text-4xl mb-4 text-white"></i>
                <h2 class="text-xl font-medium text-white">How can I help you today?</h2>
                <p class="text-sm mt-2 max-w-sm">Legends AI Master Pro - Vercel Edition</p>
            </div>
        </div>

        <div class="absolute bottom-0 w-full p-4 md:p-8 bg-gradient-to-t from-black via-black to-transparent">
            <div class="max-w-3xl mx-auto input-container flex items-end gap-2">
                <button class="p-2 text-gray-400 hover:text-white transition"><i class="fas fa-paperclip"></i></button>
                <textarea id="userInput" class="flex-1 bg-transparent border-none text-white resize-none max-h-[200px] py-2 text-sm" placeholder="Message Legends AI..." rows="1"></textarea>
                <button id="sendBtn" class="p-2 bg-white text-black rounded-lg hover:bg-gray-200 transition"><i class="fas fa-arrow-up"></i></button>
            </div>
            <div class="text-center text-[10px] text-gray-500 mt-3">Legends AI can make mistakes. Consider verifying important information.</div>
        </div>
    </main>

    <script>
        let chatHistory = [];
        
        document.getElementById('sendBtn').onclick = sendMessage;
        document.getElementById('userInput').oninput = function() { this.style.height = 'auto'; this.style.height = this.scrollHeight + 'px'; };
        document.getElementById('userInput').onkeydown = (e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } };

        async function sendMessage() {
            const val = document.getElementById('userInput').value.trim(); if(!val) return;
            
            // Eğer ilk mesajsa ortadaki logoyu sil
            if(chatHistory.length === 0) document.getElementById('chat-container').innerHTML = '';
            
            document.getElementById('userInput').value = ""; document.getElementById('userInput').style.height = 'auto';
            addMsgUI(val, 'user');
            chatHistory.push({role: "user", content: val});
            
            const loadId = "ai_" + Date.now();
            document.getElementById('chat-container').innerHTML += `<div id="${loadId}" class="msg-ai text-gray-400 text-sm"><i class="fas fa-circle-notch fa-spin mr-2"></i> Thinking...</div>`;
            document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;

            try {
                const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ messages: chatHistory }) });
                const data = await res.json();
                document.getElementById(loadId).remove();
                addMsgUI(data.answer, 'assistant');
                chatHistory.push({role: "assistant", content: data.answer});
            } catch(e) { document.getElementById(loadId).innerHTML = "❌ Error"; }
        }

        function addMsgUI(t, r) {
            const d = document.createElement('div'); 
            d.className = r === 'user' ? 'msg-user text-sm' : 'msg-ai text-sm flex gap-4';
            
            if(r === 'user') {
                d.innerHTML = t;
            } else {
                d.innerHTML = `<div class="w-8 h-8 rounded-full border border-[#333] flex items-center justify-center flex-shrink-0 bg-[#111]"><i class="fas fa-cube text-xs text-white"></i></div><div class="flex-1 markdown-body">${marked.parse(t)}</div>`;
            }
            
            document.getElementById('chat-container').appendChild(d);
            
            if(r === 'assistant') {
                d.querySelectorAll('pre').forEach(pre => {
                    const code = pre.innerText, acts = document.createElement('div'); acts.className = 'code-actions';
                    
                    const up = document.createElement('button'); up.className='code-btn'; up.innerHTML='<i class="fas fa-history"></i> Güncelle v2';
                    up.onclick = () => { document.getElementById('userInput').value = `Mevcut kodu bozmadan şunları ekle:\\n\\n\`\`\`\\n${code}\\n\`\`\``; document.getElementById('userInput').focus(); };
                    
                    const cp = document.createElement('button'); cp.className='code-btn'; cp.innerHTML='<i class="fas fa-copy"></i> Kopyala';
                    cp.onclick = () => { navigator.clipboard.writeText(code); cp.innerHTML='<i class="fas fa-check"></i>'; setTimeout(()=>cp.innerHTML='<i class="fas fa-copy"></i> Kopyala', 2000); };
                    
                    acts.append(up, cp); pre.appendChild(acts);
                });
            }
            document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
        }

        document.getElementById('openSidebar').onclick = () => document.getElementById('sidebar').classList.add('open');
        document.getElementById('closeSidebar').onclick = () => document.getElementById('sidebar').classList.remove('open');
        document.getElementById('newChatBtn').onclick = () => { chatHistory = []; document.getElementById('chat-container').innerHTML = '<div class="flex flex-col items-center justify-center h-full text-center text-gray-500"><i class="fas fa-cube text-4xl mb-4 text-white"></i><h2 class="text-xl font-medium text-white">How can I help you today?</h2></div>'; };
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

