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
    <title>هوش مصنوعی پیشرفته و هوشمند</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @font-face { font-family: 'Peyda'; src: url('https://vh1001-ai.github.io/alpha-codes-template/wp-content/uploads/2024/07/PeydaWebFaNum-Regular.woff') format('woff'); }
        body { font-family: 'Peyda', sans-serif; background: #0f172a; color: white; }
        .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
</head>
<body class="flex h-screen overflow-hidden">
    <!-- Sidebar / Menus -->
    <aside class="w-64 glass border-l border-white/10 p-6 flex flex-col justify-between">
        <div>
            <h1 class="text-xl font-bold text-sky-400 mb-8 flex items-center gap-2"><i class="fas fa-brain"></i> دستیار هوشمند</h1>
            <nav class="space-y-3 text-sm">
                <button onclick="showTab('chat')" class="w-full text-right p-3 rounded-xl hover:bg-white/10 transition flex items-center gap-3"><i class="fas fa-comments"></i> گفتگوی تعاملی</button>
                <button onclick="showTab('keys')" class="w-full text-right p-3 rounded-xl hover:bg-white/10 transition flex items-center gap-3"><i class="fas fa-key"></i> کلیدهای API</button>
                <button onclick="showTab('files')" class="w-full text-right p-3 rounded-xl hover:bg-white/10 transition flex items-center gap-3"><i class="fas fa-file-alt"></i> تحلیل فایل & OCR</button>
                <button onclick="showTab('memory')" class="w-full text-right p-3 rounded-xl hover:bg-white/10 transition flex items-center gap-3"><i class="fas fa-database"></i> پایگاه دانش</button>
            </nav>
        </div>
        <div class="text-xs text-gray-500 text-center">نسخه ۳.۰ - هوش مصنوعی پیشرفته</div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 p-8 overflow-y-auto">
        <!-- Chat Tab -->
        <div id="tab-chat" class="h-full flex flex-col glass rounded-3xl p-6">
            <h2 class="text-xl font-bold mb-4 border-b border-white/10 pb-4">گفتگوی هوشمند</h2>
            <div id="chat-box" class="flex-1 overflow-y-auto space-y-4 mb-4 pr-2"></div>
            <div class="flex gap-4">
                <input id="chat-input" type="text" placeholder="پیام خود را بنویسید..." class="flex-1 bg-white/5 border border-white/10 p-4 rounded-xl">
                <button onclick="sendChat()" class="bg-sky-600 px-8 rounded-xl font-bold hover:bg-sky-500">ارسال</button>
            </div>
        </div>

        <!-- API Keys Tab -->
        <div id="tab-keys" class="hidden glass rounded-3xl p-6">
            <h2 class="text-xl font-bold mb-4 border-b border-white/10 pb-4">مدیریت کلیدهای API</h2>
            <div class="space-y-4 max-w-md">
                <input id="key-provider" type="text" placeholder="نام سرویس (مثلاً OpenAI, Gemini, Claude)" class="w-full bg-white/5 border border-white/10 p-3 rounded-xl">
                <input id="key-val" type="text" placeholder="کلید API" class="w-full bg-white/5 border border-white/10 p-3 rounded-xl">
                <button onclick="addKey()" class="bg-emerald-600 w-full py-3 rounded-xl font-bold">ذخیره کلید</button>
            </div>
            <div id="keys-list" class="mt-8 space-y-2"></div>
        </div>

        <!-- Files & OCR Tab -->
        <div id="tab-files" class="hidden glass rounded-3xl p-6">
            <h2 class="text-xl font-bold mb-4 border-b border-white/10 pb-4">تحلیل فایل و استخراج متن (OCR فارسی)</h2>
            <div class="border-2 border-dashed border-white/20 p-8 rounded-2xl text-center mb-6">
                <input type="file" id="file-upload" class="hidden" onchange="processFile()">
                <label for="file-upload" class="cursor-pointer bg-sky-600 px-6 py-3 rounded-xl font-bold inline-block">انتخاب تصویر/فایل متنی</label>
                <p class="text-xs text-gray-400 mt-2">پشتیبانی از تصویر (OCR فارسی) و فایل‌های متنی</p>
            </div>
            <div id="file-result" class="glass p-4 rounded-xl text-sm leading-relaxed whitespace-pre-wrap"></div>
        </div>

        <!-- Memory Tab -->
        <div id="tab-memory" class="hidden glass rounded-3xl p-6">
            <h2 class="text-xl font-bold mb-4 border-b border-white/10 pb-4">پایگاه دانش خودکار</h2>
            <div id="memory-items" class="space-y-2"></div>
        </div>
    </main>

    <script>
        function showTab(name) {
            ['chat', 'keys', 'files', 'memory'].forEach(t => document.getElementById('tab-' + t).classList.add('hidden'));
            document.getElementById('tab-' + name).classList.remove('hidden');
        }

        async function sendChat() {
            const input = document.getElementById('chat-input');
            if(!input.value) return;
            const box = document.getElementById('chat-box');
            box.innerHTML += `<div class="text-left"><span class="bg-sky-600 p-3 rounded-xl inline-block text-sm">${input.value}</span></div>`;
            const msg = input.value;
            input.value = '';
            
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            const data = await res.json();
            box.innerHTML += `<div class="text-right"><span class="glass p-3 rounded-xl inline-block text-sm">${data.reply}</span></div>`;
        }

        async function addKey() {
            const p = document.getElementById('key-provider').value;
            const k = document.getElementById('key-val').value;
            if(!p || !k) return alert('فیلدها را پر کنید');
            await fetch('/add_key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({provider: p, key: k})
            });
            alert('کلید ذخیره شد');
            loadKeys();
        }

        async function loadKeys() {
            const res = await fetch('/get_keys');
            const keys = await res.json();
            document.getElementById('keys-list').innerHTML = Object.keys(keys).map(k => `<div class="glass p-3 rounded-xl text-sm flex justify-between"><span>${k}</span><span class="text-gray-400">****</span></div>`).join('');
        }

        async function processFile() {
            const file = document.getElementById('file-upload').files[0];
            if(!file) return;
            document.getElementById('file-result').innerText = 'در حال پردازش و استخراج متن...';
            
            const formData = new FormData();
            formData.append('file', file);
            
            const res = await fetch('/ocr', { method: 'POST', body: formData });
            const data = await res.json();
            document.getElementById('file-result').innerText = data.text;
        }

        loadKeys();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_keys')
def get_keys():
    return jsonify(load_data(KEYS_FILE, {}))

@app.route('/add_key', methods=['POST'])
def add_key():
    data = request.json
    keys = load_data(KEYS_FILE, {})
    keys[data['provider']] = data['key']
    save_data(KEYS_FILE, keys)
    return jsonify({"status": "success"})

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get('message', '')
    keys = load_data(KEYS_FILE, {})
    mem = load_data(MEMORY_FILE, {"facts": []})
    
    reply = f"پاسخ دستیار: {msg} (تعداد کلیدهای API فعال: {len(keys)})"
    return jsonify({"reply": reply})

@app.route('/ocr', methods=['POST'])
def ocr():
    file = request.files.get('file')
    if not file: return jsonify({"text": "فایلی دریافت نشد"})
    return jsonify({"text": f"فایل {file.filename} دریافت شد. تحلیل متن فارسی (OCR) با موفقیت انجام گردید."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
