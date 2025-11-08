import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db import has_claimed, save_claim
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from spl.token.instructions import transfer_checked, get_associated_token_address
from spl.token.constants import TOKEN_PROGRAM_ID

# Telegram token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN or not TOKEN.startswith("799"):
    raise ValueError("TELEGRAM_BOT_TOKEN is missing or invalid.")

CHANNEL_ID = -1002161990185

# Solana setup
key_array = json.loads(os.getenv("PRIVATE_KEY"))
sender = Keypair.from_bytes(bytes(key_array))
client = AsyncClient("https://api.mainnet-beta.solana.com")
MINT = Pubkey.from_string("CLX3PRe79QGUzKT1ZwNA5nVcPb4SEGoqJD5oTwJMpump")
DECIMALS = 9

async def send_trumpdead(recipient_wallet: str, amount: float = 100):
    recipient = Pubkey.from_string(recipient_wallet)
    sender_token_account = get_associated_token_address(sender.pubkey(), MINT)
    recipient_token_account = get_associated_token_address(recipient, MINT)

    tx = Transaction()
    ix = transfer_checked(
        source=sender_token_account,
        mint=MINT,
        dest=recipient_token_account,
        owner=sender.pubkey(),
        amount=int(amount * (10 ** DECIMALS)),
        decimals=DECIMALS,
        program_id=TOKEN_PROGRAM_ID,
        signers=[]
    )
    tx.add(ix)

    response = await client.send_transaction(tx, sender)
    return response.value  # tx signature

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

    if not await check_subscription(user_id, app):
        await update.message.reply_text("Please join @trump_dead_coin to receive your $TRUMPDEAD tokens.")
        return

    if has_claimed(user_id):
        await update.message.reply_text("You've already claimed your $TRUMPDEAD.")
        return

    args = context.args
    if args:
        address = args[0]
        try:
            tx_sig = await send_trumpdead(address)
            save_claim(user_id, address)
            await update.message.reply_text(f"100 $TRUMPDEAD sent to {address} 🚀\nTx: https://solscan.io/tx/{tx_sig}")
        except Exception as e:
            await update.message.reply_text(f"Error sending tokens: {str(e)}")
    else:
        await update.message.reply_text("Send: /wallet <your Solana address> to claim your $TRUMPDEAD.")

# Запуск приложения
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("wallet", wallet))
app.run_polling()

