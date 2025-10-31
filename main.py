import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from recognizer import recognize_audio, recognize_music
import yt_dlp

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUDD_TOKEN = os.getenv("AUDD_API_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎧 Sernavo Bot 3.0 ga xush kelibsiz!\n\n"
        "🎵 Qo‘shiq yoki qo‘shiqchi nomini yoz — topib beraman.\n"
        "🎙️ Ovozli xabar yubor — tanib beraman.\n"
        "📸 Instagram yoki YouTube link yubor — yuklab beraman!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "instagram.com" in text or "youtube.com" in text or "youtu.be" in text:
        await download_media(update, text)
        return
    await search_youtube(update, text)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    await file.download_to_drive("voice.ogg")

    result_text = recognize_audio("voice.ogg")
    if result_text:
        await update.message.reply_text(f"🗣️ Siz aytdingiz: {result_text}")
        await search_youtube(update, result_text)
    else:
        song_info = recognize_music("voice.ogg", AUDD_TOKEN)
        if song_info:
            await update.message.reply_text(
                f"🎵 Topildi: {song_info['artist']} – {song_info['title']}"
            )
            await search_youtube(update, f"{song_info['artist']} {song_info['title']}")
        else:
            await update.message.reply_text("❌ Qo‘shiqni aniqlab bo‘lmadi.")

async def search_youtube(update: Update, query: str):
    search_url = f"ytsearch5:{query}"
    ydl_opts = {"quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_url, download=False)
        videos = info.get("entries", [])

    if not videos:
        await update.message.reply_text("❌ Hech narsa topilmadi.")
        return

    msg = f"🎤 {query} uchun topilgan qo‘shiqlar:\n\n"
    buttons = []
    for i, v in enumerate(videos, start=1):
        msg += f"{i}. {v['title']}\n"
        buttons.append([InlineKeyboardButton(str(i), callback_data=f"dl_{v['id']}")])

    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons))

async def download_media(update: Update, url: str):
    await update.message.reply_text("⬇️ Yuklanmoqda... biroz kuting.")
    ydl_opts = {"format": "mp4", "outtmpl": "video.%(ext)s", "quiet": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        await update.message.reply_video(open("video.mp4", "rb"))
        os.remove("video.mp4")
        await update.message.reply_text("✅ Video yuborildi.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Xatolik: {e}")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    vid_id = query.data.replace("dl_", "")
    url = f"https://www.youtube.com/watch?v={vid_id}"

    await query.edit_message_text("🎧 Yuklanmoqda...")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "song.%(ext)s",
        "postprocessors": [{"key": "FFmpegExtractAudio","preferredcodec": "mp3","preferredquality": "192"}],
        "quiet": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        await query.message.reply_audio(open("song.mp3", "rb"), title=info["title"])
        os.remove("song.mp3")
    except Exception as e:
        await query.message.reply_text(f"⚠️ Xatolik: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()