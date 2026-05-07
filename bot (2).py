import os
import time
import requests
import yt_dlp
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

def send_audio(chat_id, filepath):
    with open(filepath, 'rb') as f:
        requests.post(f"{API}/sendAudio", data={"chat_id": chat_id}, files={"audio": f}, timeout=120)

def send_video(chat_id, filepath):
    with open(filepath, 'rb') as f:
        requests.post(f"{API}/sendVideo", data={"chat_id": chat_id}, files={"video": f}, timeout=120)

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '/tmp/audio.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def download_video(url):
    ydl_opts = {
        'format': 'best[height<=480]',
        'outtmpl': '/tmp/video.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info), info

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
                audio_file = download_audio(text)
                send_audio(chat_id, audio_file)
                os.remove(audio_file)

                video_file, info = download_video(text)
                send_video(chat_id, video_file)
                os.remove(video_file)

                title = info.get('title', '').replace(' ', '+')
                send_message(chat_id, f"🎶 O'xshash qo'shiqlar:\nhttps://www.youtube.com/results?search_query={title}")
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
