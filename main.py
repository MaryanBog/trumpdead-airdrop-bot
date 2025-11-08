import asyncio
import logging
import os
import httpx
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solana.rpc.providers.async_http import AsyncHTTPProvider
from solana.system_program import transfer, TransferParams
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY is missing")

session = httpx.AsyncClient(timeout=30.0)
client = AsyncHTTPProvider("https://api.mainnet-beta.solana.com", session)

sender = Keypair.from_base58_string(PRIVATE_KEY)

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pubkey = str(sender.pubkey())
    await update.message.reply_text(f"Your wallet:\n`{pubkey}`", parse_mode="Markdown")

async def airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /airdrop <recipient_address>")
        return

    try:
        recipient = Pubkey.from_string(context.args[0])
        ix = transfer(
            TransferParams(
                from_pubkey=sender.pubkey(),
                to_pubkey=recipient,
                lamports=10000
            )
        )
        blockhash = await client.get_latest_blockhash()
        tx = Transaction([ix], sender.pubkey(), blockhash.value.blockhash)
        sig = await client.send_transaction(tx, sender)
        await update.message.reply_text(f"Transaction sent:\nhttps://solscan.io/tx/{sig}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def main():
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN is missing")

    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("airdrop", airdrop))
    await app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
