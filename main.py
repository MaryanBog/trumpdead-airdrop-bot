import asyncio
import logging
import os
import httpx
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.transaction import Transaction
from solana.rpc.providers.async_http import AsyncHTTPProvider
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- ENV ---
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY is missing")

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")

# --- Solana ---
session = httpx.AsyncClient(timeout=30.0)
client = AsyncHTTPProvider("https://api.mainnet-beta.solana.com", session)
sender = Keypair.from_base58_string(PRIVATE_KEY)

# --- Handlers ---
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pubkey = str(sender.pubkey())
    await update.message.reply_text(f"Your wallet:\n`{pubkey}`", parse_mode="MarkdownV2")

async def airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /airdrop <recipient_address>")
        return

    try:
        recipient = Pubkey.from_string(context.args[0])
    except:
        await update.message.reply_text("Invalid address.")
        return

    try:
        ix = transfer(TransferParams(
            from_pubkey=sender.pubkey(),
            to_pubkey=recipient,
            lamports=10_000
        ))

        blockhash = await client.get_latest_blockhash()
        tx = Transaction.new_with_payer([ix], sender.pubkey())
        tx.recent_blockhash = blockhash.value.blockhash
        tx.sign(sender)

        sig = await client.send_transaction(tx)
        await update.message.reply_text(f"Sent!\nhttps://solscan.io/tx/{sig.value}")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# --- Main ---
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("airdrop", airdrop))
    await app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
