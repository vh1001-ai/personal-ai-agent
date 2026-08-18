import os
import json
from flask import Flask, render_template_string, request, jsonify
import requests
import threading
import time

app = Flask(__name__)
MEMORY_FILE = "knowledge_base.json"

# Config - In production, use env vars
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"facts": [], "preferences": []}

def save_memory(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Telegram Polling
def telegram_bot():
    if not TELEGRAM_BOT_TOKEN: return
    offset = None
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            res = requests.get(url, params=params).json()
            if res.get("result"):
                for update in res["result"]:
                    offset = update["update_id"] + 1
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"].get("text", "")
                    
                    # Logic
                    reply = f"هوش مصنوعی شما دریافت کرد: {text}. دانش آموخته شده: {len(load_memory()['facts'])} فکت."
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", 
                                  json={"chat_id": chat_id, "text": reply})
        except: time.sleep(5)

if TELEGRAM_BOT_TOKEN:
    threading.Thread(target=telegram_bot, daemon=True).start()

# AI Core with API Integration
def get_ai_reply(msg, facts):
    if not OPENAI_API_KEY:
        return f"پاسخ پیش‌فرض (بدون API Key): {msg}. دانش: {', '.join(facts[-3:])}"
    
    # OpenAI integration
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": f"Facts: {facts}"}, {"role": "user", "content": msg}]
    }
    try:
        r = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        return r.json()["choices"][0]["message"]["content"]
    except: return "خطا در اتصال به هوش مصنوعی."

@app.route('/')
def index():
    return "AI Core Active. Go to /chat or set up Telegram Bot."

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get('message', '')
    mem = load_memory()
    return jsonify({"reply": get_ai_reply(msg, mem['facts'])})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
