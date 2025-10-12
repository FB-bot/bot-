from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "হ্যালো! আমি তোমার ওয়েলকাম বট। 👋\nএটি Railway-এ হোস্ট করা হয়েছে।"
    )

# Bot চালানোর প্রধান ফাংশন
if __name__ == "__main__":
    app = ApplicationBuilder().token("8472535428:AAGAcUvGClisEF9Kr0MsaKLGw5Je_AY4JVU").build()

    # /start কমান্ড যোগ করা
    app.add_handler(CommandHandler("start", start))

    print("Bot চালু হয়েছে...")
    app.run_polling()
