from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
from bs4 import BeautifulSoup
import urllib.parse

# توکن رباتت رو از BotFather بگیر و جایگزین کن
TELEGRAM_BOT_TOKEN = '8215713584:AAGcZsELnN0L-VGcLZ8zIZqRAPK6e26_LM4'

# تابع جستجو در ترب
def search_torob(product_name):
    query = urllib.parse.quote(product_name)
    url = f"https://torob.com/search/?query={query}&sort=price"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    results = soup.select('a[href^="/p/"]')

    if not results:
        return "نتیجه‌ای پیدا نشد."

    message = "ارزان‌ترین نتایج در ترب:\n\n"
    count = 0

    for result in results:
        title = result.get_text(strip=True)
        link = "https://torob.com" + result['href']
        message += f"{title}\n{link}\n\n"
        count += 1
        if count >= 5:
            break

    return message

# پیام خوش‌آمد
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! نام محصولی که می‌خواهی قیمتش را در ترب ببینی وارد کن.")

# پردازش پیام‌های متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await update.message.reply_text("در حال جستجو در ترب ...")
    result = search_torob(user_input)
    await update.message.reply_text(result)

# اجرای ربات
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("ربات فعال شد.")
    app.run_polling()

if __name__ == '__main__':
    main()
