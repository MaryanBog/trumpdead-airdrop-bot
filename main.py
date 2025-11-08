import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- ENV ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")

# --- Конфиг ---
CHANNEL_LINK = "t.me/trump_dead_coin"
AIRDROP_AMOUNT = 100
claimed_users = set()

# --- Проверка подписки ---
async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member("@trump_dead_coin", update.effective_user.id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🔥 $TRUMPDEAD Airdrop\n\n"
        f"1. Подпишись: {CHANNEL_LINK}\n"
        f"2. /airdrop <адрес>\n\n"
        f"Получи {AIRDROP_AMOUNT} $TRUMPDEAD!"
    )

async def airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in claimed_users:
        await update.message.reply_text("❌ Уже получал!")
        return

    if not await is_subscribed(update, context):
        await update.message.reply_text(f"⚠️ Подпишись: {CHANNEL_LINK}")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ /airdrop <адрес>")
        return

    wallet = context.args[0].strip()
    if len(wallet) < 32 or len(wallet) > 44:
        await update.message.reply_text("❌ Неверный адрес!")
        return

    claimed_users.add(user_id)
    await update.message.reply_text(
        f"🎉 Airdrop отправлен!\n\n"
        f"👤 {update.effective_user.first_name}\n"
        f"💰 `{wallet}`\n"
        f"🪙 {AIRDROP_AMOUNT} $TRUMPDEAD\n"
        f"🔗 https://solscan.io/tx/sim_{user_id}\n\n"
        f"Скоро придут! (симуляция)",
        parse_mode="Markdown"
    )

# --- Запуск без asyncio.run ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("airdrop", airdrop))
    print("🤖 Бот запущен...")
    app.run_polling()
