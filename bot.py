import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ساخت سرور مجازی برای دور زدن خطای پورت Render
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# ۱. توکن دریافت شده از BotFather
BOT_TOKEN = ""8814065325:AAEgpJH-L2W7EIE0dJQPuFdQkpL1Ct2YCvI # توکن کامل خودتان را اینجا بگذارید

# ۲. آیدی عمومی گروه/کانال
REQUIRED_GROUP = "@danlowdertel"

async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_GROUP, user_id=user_id)
        return member.status not in ['left', 'kicked']
    except Exception as e:
        print(f"خطا در بررسی عضویت: {e}")
        return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_user_member(user_id, context):
        keyboard = [
            [InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{REQUIRED_GROUP.replace('@', '')}")],
            [InlineKeyboardButton("تایید عضویت", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"برای استفاده از ربات باید عضو کانال زیر شوید:\n{REQUIRED_GROUP}",
            reply_markup=reply_markup
        )
        return

    await update.message.reply_text("سلام! لینک پست اینستاگرام را بفرستید تا دانلود کنم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_user_member(user_id, context):
        await start(update, context)
        return

    url = update.message.text
    if "instagram.com" not in url:
        await update.message.reply_text("لطفاً یک لینک معتبر از اینستاگرام بفرستید.")
        return

    msg = await update.message.reply_text("در حال دانلود...")
    try:
        ydl_opts = {'format': 'best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            download_url = info.get('url')
            
        await update.message.reply_video(video=download_url)
        await msg.delete()
    except Exception as e:
        await msg.edit_text("خطا در دانلود فایل. ممکن است پیج خصوصی باشد.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
        
