from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes,
    ConversationHandler, CallbackQueryHandler
)
import requests
from bs4 import BeautifulSoup
import urllib.parse

TELEGRAM_BOT_TOKEN = '8215713584:AAGcZsELnN0L-VGcLZ8zIZqRAPK6e26_LM4'

ASK_PRODUCT = 0
user_inputs = {}

def search_torob(product_name):
    query = urllib.parse.quote(product_name)
    url = f"https://torob.com/search/?query={query}&sort=price"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.select('a[href^="/p/"]')

    if not results:
        return "❌ هیچ نتیجه‌ای یافت نشد."

    message = "🔎 *نتایج جستجو:*\n\n"
    count = 0

    for result in results:
        title = "نامشخص"
        link = "https://torob.com" + result['href']

        # پیدا کردن قیمت در divهای اطراف
        parent = result.find_parent()
        price = "نامشخص"
        if parent:
            title_h2 = parent.find_all("h2", attrs={'class' : 'ProductCard_desktop_product-name__JwqeK'})
            title_dives = parent.find_all("div", attrs={'class' : 'ProductCard_desktop_shops__mbtsF'})

            for h2 in title_h2:
                title = f"{h2.get_text(strip=True)}"
            for div in title_dives:
                title = title + f" {div.get_text(strip=True)}"

            price_divs = parent.find_all("div", attrs={'class' : 'ProductCard_desktop_product-price-text__y20OV'})
            for div in price_divs:
                if "تومان" in div.get_text():
                    price = div.get_text(strip=True)
                    break

        message += f"🛒 *{title}*\n\n💰 قیمت: {price}\n\n[مشاهده محصول]({link})\n\n\n"
        count += 1
        if count >= 5:
            break

    if count == 0:
        return "⚠️ هیچ نتیجه‌ای یافت نشد."
    return message

# شروع مکالمه
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_inputs[chat_id] = {}
    await update.message.reply_text("سلام! لطفاً نام محصول مورد نظر خود را وارد نمایید:")
    return ASK_PRODUCT

# شروع مجدد
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user_inputs[chat_id] = {}
    await query.message.reply_text("لطفاً نام محصول جدید خود را وارد نمایید:")
    return ASK_PRODUCT

# دریافت محصول
async def get_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_inputs[chat_id]['product'] = update.message.text

    await update.message.reply_text("⏳ در حال جستجو در سایت ترب...")

    product = user_inputs[chat_id].get('product')
    result = search_torob(product)

    keyboard = [
        [InlineKeyboardButton("🔁 جستجوی جدید", callback_data='restart')],
        [InlineKeyboardButton("❌ پایان", callback_data='end')],
    ]
    await update.message.reply_text(
        result,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# دکمه پایان
async def end_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("✅ عملیات جستجو به پایان رسید.\nبرای شروع مجدد، دستور /start را ارسال نمایید.")
    return ConversationHandler.END

# لغو
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔ عملیات لغو شد.")
    return ConversationHandler.END

# اجرای ربات
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(restart, pattern='^restart$')
        ],
        states={
            ASK_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(end_search, pattern='^end$'))

    print("🤖 ربات با موفقیت راه‌اندازی شد.")
    app.run_polling()

if __name__ == '__main__':
    main()
