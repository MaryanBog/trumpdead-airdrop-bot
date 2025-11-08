import asyncio
import logging
import os
import httpx
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.providers.async_http import AsyncHTTPProvider
from solana.transaction import Transaction
from solana.system_program import transfer, TransferParams
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 Получаем приватный ключ из переменной окружения
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY не задан в переменных окружения")

# 🚀 Создаём RPC-клиент вручную, без proxy
session = httpx.AsyncClient(timeout=30.0)
client = AsyncHTTPProvider("https://api.mainnet-beta.solana.com", session)

# 🧾 Загружаем отправителя
sender = Keypair.from_base58_string(PRIVATE_KEY)

# 📤 Команда /wallet — показывает адрес
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pubkey = str(sender.pubkey())
    await update.message.reply_text(f"Ваш кошелёк:\n`{pubkey}`", parse_mode="Markdown")

# 💸 Команда /airdrop <адрес> — отправляет 0.00001 SOL
async def airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Использование: /airdrop <адрес>")
        return

    try:
        recipient = Pubkey.from_string(context.args[0])
        tx = Transaction()
        tx.add(
            transfer(
                TransferParams(
                    from_pubkey=sender.pubkey(),
                    to_pubkey=recipient,
                    lamports=10000
                )
            )
        )
        sig = await client.send_transaction(tx, sender)
        await update.message.reply_text(f"Транзакция отправлена:\nhttps://solscan.io/tx/{sig}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# 🧠 Запуск Telegram-бота
async def main():
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN не задан в переменных окружения")

    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("airdrop", airdrop))
    await app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

