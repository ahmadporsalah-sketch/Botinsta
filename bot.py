import os
import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# ۱. توکن جدید دریافت شده از BotFather را اینجا بگذارید
BOT_TOKEN = "8814065325:AAEgpJH-L2W7EIE0dJQPuFdQkpL1Ct2YCvI"

# ۲. آیدی عمومی گروه (ربات باید در این گروه ادمین باشد)
REQUIRED_GROUP = "@danlowdertel"

async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_GROUP, user_id=user_id)
        return member.status not in ["left", "kicked"]
    except Exception as e:
        print(f"خطا در بررسی عضویت: {e}")
        return True

async def send_join_prompt(update: Update):
    group_link = f"https://t.me/{REQUIRED_GROUP.replace('@', '')}"
    keyboard = [
        [InlineKeyboardButton("📢 برای عضویت در گروه کلیک کنید", url=group_link)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚠️ **دسترسی محدود است!**\n\n"
        "برای استفاده از این ربات و دانلود پست‌ها، ابتدا باید عضو گروه زیر شوید:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await is_user_member(user_id, context):
        await send_join_prompt(update)
        return

    await update.message.reply_text(
        "سلام! 👋\n"
        "عضویت شما تایید شد. لینک پست یا ریلز اینستاگرام رو بفرست تا دانلود کنم."
    )

async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await is_user_member(user_id, context):
        await send_join_prompt(update)
        return

    url = update.message.text
    instagram_pattern = r'(https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[A-Za-z0-9_-]+)'
    if not re.search(instagram_pattern, url):
        return

    status_msg = await update.message.reply_text("⏳ در حال دانلود از اینستاگرام...")

    download_folder = "downloads"
    os.makedirs(download_folder, exist_ok=True)

    ydl_opts = {
        'outtmpl': f'{download_folder}/%(id)s.%(ext)s',
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        loop = asyncio.get_running_loop()
        file_path, is_video = await loop.run_in_executor(None, _download_media, url, ydl_opts)

        await status_msg.edit_text("📤 در حال آپلود به تلگرام...")

        if os.path.exists(file_path):
            with open(file_path, 'rb') as media_file:
                if is_video:
                    await update.message.reply_video(video=media_file, caption="خدمت شما! 🌹")
                else:
                    await update.message.reply_photo(photo=media_file, caption="خدمت شما! 🌹")
            
            os.remove(file_path)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ فایلی پیدا نشد.")

    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit_text("❌ خطا در دانلود! ممکن است پیج خصوصی باشد.")

def _download_media(url: str, options: dict):
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        is_video = info.get('ext') in ['mp4', 'mkv', 'webm']
        return filename, is_video

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram))

    print("✅ ربات روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
      
