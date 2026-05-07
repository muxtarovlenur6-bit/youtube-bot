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

def get_download_url(url, mode):
    r = requests.post("https://api.cobalt.tools/",
        json={"url": url, "downloadMode": mode, "videoQuality": "480"},
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=30)
    d = r.json()
    if d.get("status") in ("tunnel", "redirect", "stream"):
        return d.get("url")
    return None

def handle_update(update):
    msg = update.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "")
    if not chat_id or not text:
        return
    if "youtube.com" in text or "youtu.be" in text:
        send_message(chat_id, "⏳ Yuklanmoqda...")
        try:
            audio_url = get_download_url(text, "audio")
            if audio_url:
                requests.post(f"{API}/sendAudio",
                    data={"chat_id": chat_id},
                    files={"audio": ("audio.mp3", requests.get(audio_url, timeout=60).content)},
                    timeout=120)
            video_url = get_download_url(text, "auto")
            if video_url:
                requests.post(f"{API}/sendVideo",
                    data={"chat_id": chat_id},
                    files={"video": ("video.mp4", requests.get(video_url, timeout=60).content)},
                    timeout=120)
            if not audio_url and not video_url:
                send_message(chat_id, "❌ Yuklab bo'lmadi")
        except Exception as e:
            send_message(chat_id, f"❌ Xatolik: {e}")
    else:
        send_message(chat_id, "🔗 YouTube havolasini yuboring")

def polling():
    offset = None
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
