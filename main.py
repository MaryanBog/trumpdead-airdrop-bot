from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь /wallet <твой адрес>, чтобы получить $TRUMPDEAD.")

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        address = args[0]
        await update.message.reply_text(f"100 $TRUMPDEAD отправлены на {address} 🚀")
    else:
        await update.message.reply_text("Используй: /wallet <твой адрес>")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("wallet", wallet))

app.run_polling()
