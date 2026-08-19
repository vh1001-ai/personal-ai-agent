import os
import json
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)
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
    <title>هوش مصنوعی شخصی (مجهز به سرویس‌های رایگان)</title>
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
                <button onclick="showTab('keys')" class="w-full text-right p-3 rounded-xl hover:bg-white/10 transition flex items-center gap-3"><i class="fas fa-key"></i> تنظیم کلید API / مدل</button>
            </nav>
        </div>
        <div class="text-xs text-emerald-400 text-center bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20">حالت رایگان (بدون نیاز به کلید) فعال است!</div>
    </aside>

    <main class="flex-1 p-8 overflow-y-auto">
        <!-- Chat Tab -->
        <div id="tab-chat" class="h-full flex flex-col glass rounded-3xl p-6">
            <h2 class="text-xl font-bold mb-4 border-b border-white/10 pb-4">گفتگو با هوش مصنوعی</h2>
            <div id="chat-box" class="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
                <div class="text-right"><span class="glass p-4 rounded-2xl inline-block text-sm">سلام! من آماده‌ام. به صورت پیش‌فرض از مدل‌های رایگان استفاده می‌کنم و نیازی به وارد کردن کلید API ندارید. هر سوالی دارید بپرسید!</span></div>
            </div>
            <div class="flex gap-4">
                <input id="chat-input" type="text" placeholder="سوال خود را بپرسید..." class="flex-1 bg-white/5 border border-white/10 p-4 rounded-xl focus:outline-none focus:border-sky-500 text-sm" onkeypress="if(event.key === 'Enter') sendChat()">
                <button onclick="sendChat()" class="bg-sky-600 px-8 rounded-xl font-bold hover:bg-sky-500 text-sm">ارسال</button>
            </div>
        </div>

        <!-- Keys Tab -->
        <div id="tab-keys" class="hidden glass rounded-3xl p-6">
            <h2 class="text-xl font-bold mb-4 border-b border-white/10 pb-4">انتخاب موتور یا کلید اختصاصی</h2>
            <p class="text-xs text-gray-400 mb-6">می‌توانید از موتورهای کاملاً رایگان (پیش‌فرض) استفاده کنید یا کلید اختصاصی خود را وارد نمایید.</p>
            <div class="space-y-4 max-w-md mb-6">
                <select id="key-provider" class="w-full bg-slate-900 border border-white/10 p-3 rounded-xl text-sm">
                    <option value="Free-Pollinations">Pollinations AI (کاملاً رایگان و بدون نیاز به کلید)</option>
                    <option value="OpenAI">OpenAI (نیاز به کلید شخصی)</option>
                    <option value="Gemini">Google Gemini (نیاز به کلید شخصی)</option>
                </select>
                <input id="key-val" type="password" placeholder="اگر سرویس رایگان است، خالی بگذارید..." class="w-full bg-white/5 border border-white/10 p-3 rounded-xl text-sm">
                <button onclick="addKey()" class="bg-emerald-600 w-full py-3 rounded-xl font-bold text-sm hover:bg-emerald-500">ذخیره تنظیمات</button>
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
            const msg = input.value.trim();
            if(!msg) return;

            const box = document.getElementById('chat-box');
            box.innerHTML += `<div class="text-left"><span class="bg-sky-600 p-3 rounded-2xl inline-block text-sm">${msg}</span></div>`;
            input.value = '';
            box.scrollTop = box.scrollHeight;

            // Loading state
            const loadingId = 'loading-' + Date.now();
            box.innerHTML += `<div id="${loadingId}" class="text-right"><span class="glass p-4 rounded-2xl inline-block text-sm text-gray-400">در حال تفکر...</span></div>`;
            box.scrollTop = box.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                const data = await res.json();
                document.getElementById(loadingId).remove();
                box.innerHTML += `<div class="text-right"><span class="glass p-4 rounded-2xl inline-block text-sm leading-relaxed">${data.reply}</span></div>`;
            } catch(e) {
                document.getElementById(loadingId).remove();
                box.innerHTML += `<div class="text-right"><span class="bg-red-500/20 text-red-300 p-4 rounded-2xl inline-block text-sm">خطا در ارتباط با سرور.</span></div>`;
            }
            box.scrollTop = box.scrollHeight;
        }

        async function addKey() {
            const provider = document.getElementById('key-provider').value;
            const key = document.getElementById('key-val').value;
            await fetch('/add_key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({provider, key})
            });
            document.getElementById('keys-status').innerText = '✅ تنظیمات با موفقیت ذخیره شد!';
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
    keys = load_data(KEYS_FILE, {"provider": "Free-Pollinations", "key": ""})
    
    provider = keys.get('provider', 'Free-Pollinations')
    api_key = keys.get('key', '')
    
    try:
        if provider == "Free-Pollinations" or not api_key:
            # Using Pollinations AI public free text generation API
            url = f"https://text.pollinations.ai/{requests.utils.quote(msg)}"
            res = requests.get(url, timeout=20)
            if res.status_code == 200:
                return jsonify({"reply": res.text})
            else:
                return jsonify({"reply": "خطا در دریافت پاسخ از سرور رایگان."})
                
        elif provider == "OpenAI":
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
                return jsonify({"reply": f"خطا از OpenAI: {data.get('error', {}).get('message', 'نامشخص')}"})
                
        elif provider == "Gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": msg}]}]}
            res = requests.post(url, json=payload, timeout=15)
            data = res.json()
            if "candidates" in data:
                return jsonify({"reply": data["candidates"][0]["content"]["parts"][0]["text"]})
            else:
                return jsonify({"reply": f"خطا از Gemini: {data}"})
                
    except Exception as e:
        return jsonify({"reply": f"خطای ارتباطی: {str(e)}"})

    return jsonify({"reply": "سرویس انتخاب‌شده نامعتبر است."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
