from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db import has_claimed, save_claim

import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@trump_dead_coin"

# Проверка подписки
async def check_subscription(user_id: int, app) -> bool:
    try:
        member = await app.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send /wallet <your address> to claim $TRUMPDEAD.")

# /wallet
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    app = context.application

    # Проверка подписки
    if not await check_subscription(user_id, app):
        await update.message.reply_text("Please join @trump_dead_coin to receive your $TRUMPDEAD tokens.")
        return

    # Проверка повторной выдачи
    if has_claimed(user_id):
        await update.message.reply_text("You've already claimed your $TRUMPDEAD.")
        return

    # Обработка адреса
    args = context.args
    if args:
        address = args[0]
        save_claim(user_id, address)
        await update.message.reply_text(f"100 $TRUMPDEAD sent to {address} 🚀")
    else:
        await update.message.reply_text("Send: /wallet 0xABC123... to claim your $TRUMPDEAD.")

# Запуск
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("wallet", wallet))
app.run_polling()

