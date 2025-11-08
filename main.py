import asyncio
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

# --- БД в памяти (один airdrop на юзера) ---
claimed_users = set()

# --- Проверка подписки (бот должен быть админом канала!) ---
async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        chat_member = await context.bot.get_chat_member("@trump_dead_coin", user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🔥 $TRUMPDEAD Airdrop 🔥\n\n"
        f"1. Подпишись: {CHANNEL_LINK}\n"
        f"2. Напиши: /airdrop <твой_Solana_адрес>\n\n"
        f"Получишь {AIRDROP_AMOUNT} $TRUMPDEAD!\n"
        f"Обратный отсчёт до 2029 тикает... 💀"
    )

async def airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # 1. Уже получал?
    if user_id in claimed_users:
        await update.message.reply_text("❌ Ты уже получил airdrop!")
        return

    # 2. Подписан?
    if not await is_subscribed(update, context):
        await update.message.reply_text(f"⚠️ Сначала подпишись: {CHANNEL_LINK}")
        return

    # 3. Адрес?
    if len(context.args) != 1:
        await update.message.reply_text("❌ Использование: /airdrop <твой_адрес>")
        return

    wallet = context.args[0].strip()

    # 4. Валидация (простая)
    if len(wallet) < 32 or len(wallet) > 44:
        await update.message.reply_text("❌ Неверный Solana-адрес!")
        return

    # 5. Успех! (симуляция)
    claimed_users.add(user_id)
    await update.message.reply_text(
        f"🎉 Airdrop отправлен!\n\n"
        f"👤 Юзер: {update.effective_user.first_name}\n"
        f"💰 Адрес: `{wallet}`\n"
        f"🪙 Токены: {AIRDROP_AMOUNT} $TRUMPDEAD\n\n"
        f"🔗 TX: https://solscan.io/tx/simulated_{user_id}\n"
        f"Скоро придут! (симуляция)\n\n"
        f"💀 Обратный отсчёт тикает...",
        parse_mode="Markdown"
    )

# --- Запуск ---
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("airdrop", airdrop))
    print("🤖 Бот запущен. Ожидание команд...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
