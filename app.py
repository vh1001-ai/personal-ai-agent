from flask import Flask, render_template_string, request, jsonify
import json
import os

app = Flask(__name__)
MEMORY_FILE = "knowledge_base.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"facts": [], "preferences": []}

def save_memory(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>هوش مصنوعی شخصی من (Self-Learning AI)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @font-face { font-family: 'Peyda'; src: url('https://vh1001-ai.github.io/alpha-codes-template/wp-content/uploads/2024/07/PeydaWebFaNum-Regular.woff') format('woff'); }
        body { font-family: 'Peyda', sans-serif; background: #0b0f19; color: white; }
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .gradient-text { background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
</head>
<body class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="glass border-b border-white/10 p-4 px-8 flex justify-between items-center">
        <div class="text-xl font-bold gradient-text"><i class="fas fa-brain ml-2"></i> دستیار هوشمند شخصی (AI Core v1.0)</div>
        <div class="text-xs text-sky-400 bg-sky-500/10 px-3 py-1.5 rounded-full border border-sky-500/20">وضعیت: آماده یادگیری و پردازش</div>
    </header>

    <!-- Main Content -->
    <div class="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Chat Area -->
        <div class="lg:col-span-2 glass rounded-3xl p-6 flex flex-col h-[75vh]">
            <div id="chat-box" class="flex-1 overflow-y-auto space-y-4 pr-2 mb-4">
                <div class="flex gap-4 items-start">
                    <div class="w-10 h-10 rounded-2xl bg-sky-500/20 flex items-center justify-center text-sky-400"><i class="fas fa-robot"></i></div>
                    <div class="glass p-4 rounded-2xl max-w-[80%] text-sm leading-relaxed">
                        سلام وحید عزیز! من هوش مصنوعی شخصی شما هستم. شما می‌توانید در بخش سمت راست به من فکت، قوانین جدید یا یادگیری‌های جدید اضافه کنید تا در پاسخ‌هایم از آن‌ها استفاده کنم. چطور می‌توانم کمکتان کنم؟
                    </div>
                </div>
            </div>
            
            <div class="flex gap-2">
                <input id="user-input" type="text" placeholder="پیام خود را بنویسید..." class="flex-1 bg-white/5 border border-white/10 p-4 rounded-2xl focus:outline-none focus:border-sky-500 text-sm">
                <button onclick="sendMessage()" class="bg-sky-600 px-6 rounded-2xl font-bold hover:bg-sky-500 transition"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>

        <!-- Learning & Memory Panel -->
        <div class="glass rounded-3xl p-6 flex flex-col h-[75vh]">
            <h3 class="text-lg font-bold mb-4 text-sky-400 flex items-center gap-2"><i class="fas fa-database"></i> پایگاه دانش و یادگیری</h3>
            <p class="text-xs text-gray-400 mb-6">به هوش مصنوعی فکت‌ها یا قوانین جدید یاد بدهید تا در حافظه ماندگارش ثبت شود.</p>
            
            <div class="space-y-4 mb-6">
                <textarea id="learn-input" placeholder="مثال: ترجیح می‌دهم پاسخ‌ها کوتاه و فنی باشند..." rows="3" class="w-full bg-white/5 border border-white/10 p-3 rounded-xl text-xs focus:outline-none focus:border-sky-500"></textarea>
                <button onclick="teachAI()" class="w-full bg-emerald-600 py-3 rounded-xl font-bold text-xs hover:bg-emerald-500 transition"><i class="fas fa-graduation-cap ml-1"></i> آموزش به هوش مصنوعی</button>
            </div>

            <h4 class="text-xs font-bold text-gray-400 mb-3">حافظه آموخته‌شده اخیر:</h4>
            <div id="memory-list" class="flex-1 overflow-y-auto space-y-2 pr-2 text-xs">
                <!-- Memory items -->
            </div>
        </div>
    </div>

    <script>
        async function loadMemory() {
            const res = await fetch('/get_memory');
            const data = await res.json();
            const list = document.getElementById('memory-list');
            list.innerHTML = data.facts.map(f => `<div class="glass p-3 rounded-xl border-r-2 border-sky-400 text-gray-300">${f}</div>`).join('');
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const text = input.value.trim();
            if(!text) return;

            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML += `<div class="flex gap-4 items-start justify-end"><div class="bg-sky-600 p-4 rounded-2xl max-w-[80%] text-sm">${text}</div></div>`;
            input.value = '';

            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await res.json();
            chatBox.innerHTML += `<div class="flex gap-4 items-start"><div class="w-10 h-10 rounded-2xl bg-sky-500/20 flex items-center justify-center text-sky-400"><i class="fas fa-robot"></i></div><div class="glass p-4 rounded-2xl max-w-[80%] text-sm leading-relaxed">${data.reply}</div></div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function teachAI() {
            const input = document.getElementById('learn-input');
            const text = input.value.trim();
            if(!text) return;

            const res = await fetch('/teach', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({fact: text})
            });
            const data = await res.json();
            alert('یادگیری با موفقیت در حافظه ثبت شد!');
            input.value = '';
            loadMemory();
        }

        loadMemory();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_memory')
def get_memory():
    return jsonify(load_memory())

@app.route('/teach', methods=['POST'])
def teach():
    data = request.json
    fact = data.get('fact')
    mem = load_memory()
    if fact and fact not in mem["facts"]:
        mem["facts"].append(fact)
        save_memory(mem)
    return jsonify({"status": "success", "facts": mem["facts"]})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message', '')
    mem = load_memory()
    
    # Custom self-learning response engine
    facts_context = " ".join(mem["facts"])
    reply = f"پیام شما دریافت شد. با توجه به پایگاه دانش آموخته‌شده من ({len(mem['facts'])} قانون ثبت‌شده)، پاسخ می‌دهم: من تمام نکات شما نظیر ({facts_context[-50:]}) را در نظر گرفتم و در خدمت شما هستم!"
    
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
