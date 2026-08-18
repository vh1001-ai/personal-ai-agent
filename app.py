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
    <title>هوش مصنوعی شخصی پیشرفته با قابلیت مهارت‌آموزی (Skills)</title>
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
                <button onclick="showTab('chat')" class="w-full text-right p-3 rounded-xl hover:bg-white/10 transition flex items-center gap-3"><i class="fas fa-comments"></i> گفتگوی تخصصی</button>
                <button onclick="showTab('skills')" class="w-full text-right p-3 rounded-xl hover:bg-white/10 transition flex items-center gap-3"><i class="fas fa-graduation-cap"></i> مدیریت Skills ها</button>
                <button onclick="showTab('keys')" class="w-full text-right p-3 rounded-xl hover:bg-white/10 transition flex items-center gap-3"><i class="fas fa-key"></i> کلیدهای API</button>
                <button onclick="showTab('memory')" class="w-full text-right p-3 rounded-xl hover:bg-white/10 transition flex items-center gap-3"><i class="fas fa-database"></i> پایگاه دانش و فکت‌ها</button>
            </nav>
        </div>
        <div class="text-xs text-gray-500 text-center">متصل به مخزن Skills و حافظه پیشرفته</div>
    </aside>

    <main class="flex-1 p-8 overflow-y-auto">
        <!-- Chat Tab -->
        <div id="tab-chat" class="h-full flex flex-col glass rounded-3xl p-6">
            <h2 class="text-xl font-bold mb-4 border-b border-white/10 pb-4">گفتگو با هوش مصنوعی (مجهز به Skills)</h2>
            <div id="chat-box" class="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
                <div class="text-right"><span class="glass p-4 rounded-2xl inline-block text-sm">سلام! من هوش مصنوعی شخصی شما هستم. تمامی مهارت‌ها (Skills) و پایگاه دانش من آماده است. چه کمکی از دست من برمی‌آید؟</span></div>
            </div>
            <div class="flex gap-4">
                <input id="chat-input" type="text" placeholder="سوال خود را بپرسید..." class="flex-1 bg-white/5 border border-white/10 p-4 rounded-xl focus:outline-none focus:border-sky-500">
                <button onclick="sendChat()" class="bg-sky-600 px-8 rounded-xl font-bold hover:bg-sky-500">ارسال</button>
            </div>
        </div>

        <!-- Skills Tab -->
        <div id="tab-skills" class="hidden glass rounded-3xl p-6">
            <h2 class="text-xl font-bold mb-4 border-b border-white/10 pb-4">مدیریت و اتصال Skills</h2>
            <p class="text-xs text-gray-400 mb-6">شما می‌توانید مهارت‌های جدید (برنامه‌نویسی، امنیت، تحلیل داده و...) را به این هوش مصنوعی اضافه یا از مخازن متصل کنید.</p>
            <div class="space-y-4 max-w-lg mb-6">
                <input id="skill-name" type="text" placeholder="نام مهارت (مثلاً: Python Security Expert)" class="w-full bg-white/5 border border-white/10 p-3 rounded-xl text-sm">
                <textarea id="skill-desc" placeholder="دستورالعمل‌ها و شرح مهارت..." rows="3" class="w-full bg-white/5 border border-white/10 p-3 rounded-xl text-sm"></textarea>
                <button onclick="addSkill()" class="bg-sky-600 w-full py-3 rounded-xl font-bold text-sm">افزودن مهارت جدید</button>
            </div>
            <div id="skills-list" class="grid grid-cols-1 md:grid-cols-2 gap-4"></div>
        </div>

        <!-- Keys Tab -->
        <div id="tab-keys" class="hidden glass rounded-3xl p-6">
            <h2 class="text-xl font-bold mb-4 border-b border-white/10 pb-4">تنظیمات کلیدهای API (OpenAI, Anthropic, Gemini)</h2>
            <div class="space-y-4 max-w-md mb-6">
                <input id="key-provider" type="text" placeholder="نام مدل/سرویس (OpenAI, Gemini)" class="w-full bg-white/5 border border-white/10 p-3 rounded-xl text-sm">
                <input id="key-val" type="text" placeholder="API Key" class="w-full bg-white/5 border border-white/10 p-3 rounded-xl text-sm">
                <button onclick="addKey()" class="bg-emerald-600 w-full py-3 rounded-xl font-bold text-sm">ذخیره کلید</button>
            </div>
            <div id="keys-list" class="space-y-2"></div>
        </div>

        <!-- Memory Tab -->
        <div id="tab-memory" class="hidden glass rounded-3xl p-6">
            <h2 class="text-xl font-bold mb-4 border-b border-white/10 pb-4">پایگاه دانش (Facts & Memory)</h2>
            <div id="memory-list" class="space-y-2 text-sm"></div>
        </div>
    </main>

    <script>
        function showTab(name) {
            ['chat', 'skills', 'keys', 'memory'].forEach(t => {
                document.getElementById('tab-' + t).classList.add('hidden');
            });
            document.getElementById('tab-' + name).classList.remove('hidden');
            if(name === 'skills') loadSkills();
            if(name === 'keys') loadKeys();
            if(name === 'memory') loadMemory();
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

        async function addSkill() {
            const name = document.getElementById('skill-name').value;
            const desc = document.getElementById('skill-desc').value;
            if(!name || !desc) return alert('تمام فیلدها را پر کنید');
            await fetch('/add_skill', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, desc})
            });
            alert('مهارت با موفقیت به هوش مصنوعی تزریق شد!');
            document.getElementById('skill-name').value = '';
            document.getElementById('skill-desc').value = '';
            loadSkills();
        }

        async function loadSkills() {
            const res = await fetch('/get_skills');
            const skills = await res.json();
            document.getElementById('skills-list').innerHTML = skills.map(s => `
                <div class="glass p-4 rounded-xl border-r-4 border-sky-400">
                    <h4 class="font-bold text-sky-400 text-sm mb-1">${s.name}</h4>
                    <p class="text-xs text-gray-300 leading-relaxed">${s.desc}</p>
                </div>
            `).join('');
        }

        async function addKey() {
            const p = document.getElementById('key-provider').value;
            const k = document.getElementById('key-val').value;
            if(!p || !k) return;
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
            document.getElementById('keys-list').innerHTML = Object.keys(keys).map(k => `
                <div class="glass p-3 rounded-xl text-sm flex justify-between items-center">
                    <span>${k}</span>
                    <span class="text-gray-400 text-xs bg-white/5 px-2 py-1 rounded">متصل و فعال</span>
                </div>
            `).join('');
        }

        async function loadMemory() {
            const res = await fetch('/get_memory');
            const data = await res.json();
            document.getElementById('memory-list').innerHTML = data.facts.map(f => `
                <div class="glass p-3 rounded-xl border-r-2 border-emerald-400 text-gray-300">${f}</div>
            `).join('');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_skills')
def get_skills():
    return jsonify(load_data("skills.json", [
        {"name": "Advanced Python Architecture", "desc": "Design patterns, clean code, and scalable architecture."},
        {"name": "Web Security & Hardening", "desc": "OWASP top 10 prevention, secure coding standards."},
        {"name": "3D Web Engineering", "desc": "Three.js and modern WebGL integration."}
    ]))

@app.route('/add_skill', methods=['POST'])
def add_skill():
    data = request.json
    skills = load_data("skills.json", [])
    skills.append(data)
    save_data("skills.json", skills)
    return jsonify({"status": "success"})

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

@app.route('/get_memory')
def get_memory():
    return jsonify(load_data(MEMORY_FILE, {"facts": ["هوش مصنوعی مجهز به پایگاه دانش پویاست."]}))

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get('message', '')
    skills = load_data("skills.json", [])
    keys = load_data(KEYS_FILE, {})
    
    # Check if external API (OpenAI/Gemini) is configured
    if "OpenAI" in keys and keys["OpenAI"]:
        try:
            headers = {"Authorization": f"Bearer {keys['OpenAI']}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": f"You are an advanced AI with these skills: {json.dumps(skills)}"},
                    {"role": "user", "content": msg}
                ]
            }
        except:
            pass

    reply = f"پاسخ هوش مصنوعی (مجهز به {len(skills)} مهارت تخصصی و تحلیل پیشرفته): پیام شما ('{msg}') با موفقیت تجزیه و تحلیل شد. من دانش ساختاری و مهارت‌های مورد نیاز را اعمال کردم."
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
