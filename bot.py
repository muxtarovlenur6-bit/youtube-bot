import os, time, requests, logging, threading
from flask import Flask

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot ishlayapti!"

def run_web():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def send_message(chat_id, text):
    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text})

def handle_update(update):
    msg = update.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "")
    if not chat_id or not text:
        return

    if "youtube.com" in text or "youtu.be" in text:
        send_message(chat_id, "⏳ Yuklanmoqda, biroz kuting...")
        try:
            audio_url = f"https://robotilab.online/download-api/yt/audio?url={text}"
            content = requests.get(audio_url, timeout=90).content
            requests.post(f"{API}/sendAudio",
                data={"chat_id": chat_id},
                files={"audio": ("audio.mp3", content, "audio/mpeg")},
                timeout=120)
            send_message(chat_id, "✅ Audio yuborildi!")
        except Exception as e:
            logging.error(f"Xatolik: {e}")
            send_message(chat_id, f"❌ Xatolik: {e}")
    else:
        send_message(chat_id, "🔗 YouTube havolasini yuboring")

def polling():
    offset = None
    logging.info("Bot polling boshlandi ✅")
    while True:
        try:
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset
            data = requests.get(f"{API}/getUpdates", params=params, timeout=40).json()
            for u in data.get("result", []):
                offset = u["update_id"] + 1
                threading.Thread(target=handle_update, args=(u,)).start()
        except Exception as e:
            logging.error(e)
            time.sleep(5)

threading.Thread(target=run_web, daemon=True).start()
polling()
