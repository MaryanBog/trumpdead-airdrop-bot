import asyncio
import logging
import httpx
from solana.rpc.providers.async_http import AsyncHTTPProvider
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 Приватный ключ в base58-строке
import os

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY is not set in environment variables")

# 🚀 Создаём RPC-клиент вручную, без proxy
session = httpx.AsyncClient(timeout=30.0)
client = AsyncHTTPProvider("https://api.mainnet-beta.solana.com", session)

# 🧾 Загружаем отправителя
sender = Keypair.from_base58_string(PRIVATE_KEY)

# 📤 Команда /wallet — показывает адрес
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pubkey = str(sender.public_key)
    await update.message.reply_text(f"Your wallet:\n`{pubkey}`", parse_mode="Markdown")

# 💸 Команда /airdrop <адрес> — отправляет 0.00001 SOL
async def airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /airdrop <recipient_address>")
        return

    try:
        recipient = PublicKey(context.args[0])
        tx = Transaction()
        tx.add(
            transfer(
                TransferParams(
                    from_pubkey=sender.public_key,
                    to_pubkey=recipient,
                    lamports=10000  # 0.00001 SOL
                )
            )
        )
        sig = await client.send_transaction(tx, sender, opts={"skip_preflight": True})
        await update.message.reply_text(f"Transaction sent:\nhttps://solscan.io/tx/{sig}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# 🧠 Запуск Telegram-бота
async def main():
    app = ApplicationBuilder().token("вставь_сюда_токен_бота").build()
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("airdrop", airdrop))
    await app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

