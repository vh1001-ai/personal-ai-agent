import os
import json
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)
MEMORY_FILE = "knowledge_base.json"
KEYS_FILE = "api_keys.json"

def load_data(file, default):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def save_data(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>هوش مصنوعی شخصی (متصل به OpenAI & Gemini)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @font-face { font-family: 'Peyda'; src: url('https://vh1001-ai.github.io/alpha-codes-template/wp-content/uploads/2024/07/PeydaWebFaNum-Regular.woff') format('woff'); }
        body { font-family: 'Peyda', sans-serif; background: #0b0f19; color: white; }
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    </style>
</head>
<body class="flex h-screen overflow-hidden">
    <aside class="w-72 glass border-l border-white/10 p-6 flex flex-col justify-between">
        <div>
            <h1 class="text-xl font-bold text-sky-400 mb-8 flex items-center gap-2"><i class="fas fa-brain"></i> هوش مصنوعی شخصی</h1>
            <nav class="space-y-3 text-sm">
                <button onclick="showTab('chat')" class="w-full text-right p-3 rounded-xl hover:bg-white/10 transition flex items-center gap-3"><i class="fas fa-comments"></i> گفتگوی هوشمند</button>
                <button onclick="showTab('keys')" class="w-full text-right p-3 rounded-xl hover:bg-white/10 transition flex items-center gap-3"><i class="fas fa-key"></i> تنظیم کلید API</button>
            </nav>
        </div>
        <div class="text-xs text-gray-500 text-center">متصل به سرویس‌های اصلی</div>
    </aside>

    <main class="flex-1 p-8 overflow-y-auto">
        <!-- Chat Tab -->
        <div id="tab-chat" class="h-full flex flex-col glass rounded-3xl p-6">
            <h2 class="text-xl font-bold mb-4 border-b border-white/10 pb-4">گفتگو با هوش مصنوعی اصلی</h2>
            <div id="chat-box" class="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
                <div class="text-right"><span class="glass p-4 rounded-2xl inline-block text-sm">سلام! برای اینکه من به موتور هوش مصنوعی متصل شوم، لطفاً در بخش "تنظیم کلید API" یک کلید معتبر (مثلاً OpenAI یا Gemini) وارد کنید تا مستقیماً به آن متصل شوم.</span></div>
            </div>
            <div class="flex gap-4">
                <input id="chat-input" type="text" placeholder="سوال خود را بپرسید..." class="flex-1 bg-white/5 border border-white/10 p-4 rounded-xl focus:outline-none focus:border-sky-500 text-sm">
                <button onclick="sendChat()" class="bg-sky-600 px-8 rounded-xl font-bold hover:bg-sky-500 text-sm">ارسال</button>
            </div>
        </div>

        <!-- Keys Tab -->
        <div id="tab-keys" class="hidden glass rounded-3xl p-6">
            <h2 class="text-xl font-bold mb-4 border-b border-white/10 pb-4">اتصال به موتور هوش مصنوعی (API Key)</h2>
            <p class="text-xs text-gray-400 mb-6">کلید API خود را وارد کنید تا تمام پاسخ‌ها به صورت واقعی از موتور هوش مصنوعی دریافت شوند.</p>
            <div class="space-y-4 max-w-md mb-6">
                <select id="key-provider" class="w-full bg-slate-900 border border-white/10 p-3 rounded-xl text-sm">
                    <option value="OpenAI">OpenAI (ChatGPT)</option>
                    <option value="Gemini">Google Gemini</option>
                </select>
                <input id="key-val" type="password" placeholder="sk-..." class="w-full bg-white/5 border border-white/10 p-3 rounded-xl text-sm">
                <button onclick="addKey()" class="bg-emerald-600 w-full py-3 rounded-xl font-bold text-sm hover:bg-emerald-500">ذخیره و اتصال</button>
            </div>
            <div id="keys-status" class="text-xs text-sky-400"></div>
        </div>
    </main>

    <script>
        function showTab(name) {
            ['chat', 'keys'].forEach(t => document.getElementById('tab-' + t).classList.add('hidden'));
            document.getElementById('tab-' + name).classList.remove('hidden');
        }

        async function sendChat() {
            const input = document.getElementById('chat-input');
            if(!input.value) return;
            const box = document.getElementById('chat-box');
            box.innerHTML += `<div class="text-left"><span class="bg-sky-600 p-3 rounded-2xl inline-block text-sm">${input.value}</span></div>`;
            const msg = input.value;
            input.value = '';

            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            const data = await res.json();
            box.innerHTML += `<div class="text-right"><span class="glass p-4 rounded-2xl inline-block text-sm leading-relaxed">${data.reply}</span></div>`;
            box.scrollTop = box.scrollHeight;
        }

        async function addKey() {
            const provider = document.getElementById('key-provider').value;
            const key = document.getElementById('key-val').value;
            if(!key) return alert('لطفاً کلید را وارد کنید');
            await fetch('/add_key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({provider, key})
            });
            document.getElementById('keys-status').innerText = '✅ کلید ذخیره شد و هوش مصنوعی آماده پاسخ‌گویی است!';
            document.getElementById('key-val').value = '';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/add_key', methods=['POST'])
def add_key():
    data = request.json
    save_data(KEYS_FILE, data)
    return jsonify({"status": "success"})

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get('message', '')
    keys = load_data(KEYS_FILE, {})
    
    provider = keys.get('provider')
    api_key = keys.get('key')
    
    if not api_key:
        return jsonify({"reply": "⚠️ لطفاً ابتدا در منوی 'تنظیم کلید API' یک کلید معتبر (مثل OpenAI) وارد کنید تا ارتباط برقرار شود."})
    
    try:
        if provider == "OpenAI":
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": msg}]
            }
            res = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=15)
            data = res.json()
            if "choices" in data:
                return jsonify({"reply": data["choices"][0]["message"]["content"]})
            else:
                return jsonify({"reply": f"خطا از سوی OpenAI: {data.get('error', {}).get('message', 'نامشخص')}"})
                
        elif provider == "Gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": msg}]}]}
            res = requests.post(url, json=payload, timeout=15)
            data = res.json()
            if "candidates" in data:
                return jsonify({"reply": data["candidates"][0]["content"]["parts"][0]["text"]})
            else:
                return jsonify({"reply": f"خطا از سوی Gemini: {data}"})
                
    except Exception as e:
        return jsonify({"reply": f"خطای اتصال به سرور هوش مصنوعی: {str(e)}"})

    return jsonify({"reply": "سرویس پشتیبانی نمی‌شود."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
