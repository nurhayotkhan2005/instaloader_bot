from telegram import Update
from telegram.ext import Application,CommandHandler, ContextTypes,MessageHandler, filters
import os
import re
import instaloader
import html
from pathlib import Path
TOKEN = ""

L = instaloader.Instaloader(
    download_comments=False,
    save_metadata=False,
    download_video_thumbnails=False
)
async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Men Instaloderman\n" 
    "Menga instagramdan link jo'nating\n" 
    "Men sizga media fayllarni jo'nataman!")

def short_cut(url:str):
    match = re.search(r"instagram\.com/(?:p|tv|reel)/([^/?]+)",url)
    return match.group(1) if match else None

async def hanle_message(update:Update,context:ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "instagram.com" not in text:
        await update.message.reply_text("Bu link insstagramniki emas!")
        return
    shortcode = short_cut(text)
    if not shortcode:
        await update.message.reply_text("Link bo'yicha media topilmadii!")
        return

    chat_id = update.effective_chat.id
    target_dir = Path("download") / f"{chat_id}_{shortcode}"

    try:
        await update.message.reply_text("Media yuklanmoqda...")
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=target_dir)
        sent_something = False
        for file in os.listdir(target_dir):
            path = os.path.join(target_dir, file)
            if file.endswith(".mp4"):
                with open(path, "rb") as f:
                    await update.message.reply_video(video=f,
                                                    caption=f"<b>{post.owner_username}</b> tomonidan joylashtirilgan video\n\n\n"
                                                    f"{html.escape(post.caption)}",
                                                    parse_mode="HTML")
        
                    sent_something = True
            elif file.endswith((".jpg",".jpeg",".webp")):
                with open(path, "rb") as f:
                    await update.message.reply_photo(photo=f,
                                                     caption=f"<b>{post.owner_username}</b> tomonidan joylashtirilgan rasm\n\n\n"
                                                        f"{html.escape(post.caption)}",
                                                        parse_mode="HTML"
                                                )
                    sent_something = True
        if not sent_something:
            await update.message.reply_text("Media topilmadi!")
    except Exception as e:
        await update.message.reply_text(f"Xatolik yuz berdi: {e}")

    finally:
        if os.path.exists(target_dir):
            for file in os.listdir(target_dir):
                os.remove(os.path.join(target_dir,file))
            os.rmdir(target_dir)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hanle_message))
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()

     