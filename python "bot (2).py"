import os
import time
import requests
import logging
import threading
from flask import Flask

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot ishlayapti! ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

def send_message(chat_id, text):
    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text})

def send_audio(chat_id, url, title):
    try:
        data = requests.get(url, timeout=60)
        requests.post(f"{API}/sendAudio", 
            data={"chat_id": chat_id, "title": title},
            files={"audio": (f"{title}.mp3", data.content, "audio/mpeg")},
            timeout=120)
    except Exception as e:
        send_message(chat_id, f"❌ Audio yuborishda xato: {e}")

def send_video(chat_id, url, title):
    try:
        data = requests.get(url, timeout=60)
        requests.post(f"{API}/sendVideo",
            data={"chat_id": chat_id},
            files={"video": (f"{title}.mp4", data.content, "video/mp4")},
            timeout=120)
    except Exception as e:
        send_message(chat_id, f"❌ Video yuborishda xato: {e}")

def get_cobalt(url, mode="auto"):
    try:
        resp = requests.post(
            "https://api.cobalt.tools/",
            json={"url": url, "downloadMode": mode, "videoQuality": "480"},
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        data = resp.json()
        if data.get("status") in ("tunnel", "redirect", "stream"):
            return data.get("url")
        return None
    except Exception as e:
        logging.error(f"Cobalt xato: {e}")
        return None

def handle_update(update):
    try:
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        if not chat_id or not text:
            return

        if "youtube.com" in text or "youtu.be" in text:
            send_message(chat_id, "⏳ Yuklanmoqda, biroz kuting...")
            try:
                # Audio
                audio_url = get_cobalt(text, mode="audio")
                if audio_url:
                    send_audio(chat_id, audio_url, "audio")
                else:
                    send_message(chat_id, "⚠️ Audio yuklab bo'lmadi")

                # Video
                video_url = get_cobalt(text, mode="auto")
                if video_url:
                    send_video(chat_id, video_url, "video")
                else:
                    send_message(chat_id, "⚠️ Video yuklab bo'lmadi")

                # O'xshash qo'shiqlar
                search = text.replace("https://", "").replace("http://", "")
                send_message(chat_id, f"🎶 Video havolasi:\n{text}")

            except Exception as e:
                logging.error(f"Xatolik: {e}")
                send_message(chat_id, f"❌ Xatolik: {e}")
        else:
            send_message(chat_id, "🔗 Iltimos, YouTube havolasini yuboring.")
    except Exception as e:
        logging.error(f"Update xatosi: {e}")

def polling():
    offset = None
    logging.info("Bot polling boshlandi ✅")
    while True:
        try:
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset
            resp = requests.get(f"{API}/getUpdates", params=params, timeout=40)
            data = resp.json()
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                threading.Thread(target=handle_update, args=(update,)).start()
        except Exception as e:
            logging.error(f"Polling xatosi: {e}")
            time.sleep(5)

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("BOT_TOKEN kiritilmagan!")
    threading.Thread(target=run_web, daemon=True).start()
    polling()
