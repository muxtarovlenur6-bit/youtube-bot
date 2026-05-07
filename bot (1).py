import logging
import os
import asyncio
import threading
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask

# ✅ Tokenni environment variable'dan olish (xavfsizroq)
TOKEN = os.environ.get("BOT_TOKEN", "")

logging.basicConfig(level=logging.INFO)

# 🔥 Flask server (UptimeRobot / Render uchun)
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot ishlayapti! ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

# 🎵 YouTube audio yuklash
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '/tmp/audio.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

# 🎥 YouTube video yuklash (480p)
def download_video(url):
    ydl_opts = {
        'format': 'best[height<=480]',
        'outtmpl': '/tmp/video.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename, info

# 🤖 Bot xabarlarni qabul qiladi
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtube.com" in url or "youtu.be" in url:
        await update.message.reply_text("⏳ Yuklanmoqda, biroz kuting...")

        try:
            # 🎧 Audio yuborish
            audio_file = download_audio(url)
            with open(audio_file, 'rb') as f:
                await update.message.reply_audio(audio=f)
            os.remove(audio_file)  # Faylni o'chirish

            # 🎥 Video yuborish
            video_file, info = download_video(url)
            with open(video_file, 'rb') as f:
                await update.message.reply_video(video=f)
            os.remove(video_file)  # Faylni o'chirish

            # 🔍 O'xshash qo'shiqlar
            title = info.get('title', '')
            search_url = f"https://www.youtube.com/results?search_query={title.replace(' ', '+')}"
            await update.message.reply_text(f"🎶 O'xshash qo'shiqlar:\n{search_url}")

        except Exception as e:
            logging.error(f"Xatolik: {e}")
            await update.message.reply_text(f"❌ Xatolik yuz berdi: {e}")
    else:
        await update.message.reply_text("🔗 Iltimos, YouTube havolasini yuboring.")

# 🚀 Botni ishga tushirish
async def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable o'rnatilmagan!")

    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Bot ishga tushdi ✅")
    await bot_app.run_polling()

if __name__ == "__main__":
    # Flask'ni alohida thread'da ishga tushiramiz
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()

    # Botni ishga tushiramiz
    asyncio.run(main())
