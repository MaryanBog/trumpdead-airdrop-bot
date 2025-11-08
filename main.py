import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- ENV ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")

# --- Config ---
CHANNEL_LINK = "t.me/trump_dead_coin"
AIRDROP_AMOUNT = 100
claimed_users = set()  # In-memory DB: one airdrop per user

# --- Subscription check (bot must be admin in the channel) ---
async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member("@trump_dead_coin", update.effective_user.id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# --- Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🔥 $TRUMPDEAD Airdrop\n\n"
        f"1. Subscribe: {CHANNEL_LINK}\n"
        f"2. Use: /airdrop <your_wallet>\n\n"
        f"You will get {AIRDROP_AMOUNT} $TRUMPDEAD!"
    )

async def airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in claimed_users:
        await update.message.reply_text("❌ Already claimed!")
        return

    if not await is_subscribed(update, context):
        await update.message.reply_text(f"⚠️ Subscribe first: {CHANNEL_LINK}")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /airdrop <wallet>")
        return

    wallet = context.args[0].strip()
    if len(wallet) < 32 or len(wallet) > 44:
        await update.message.reply_text("❌ Invalid Solana address!")
        return

    claimed_users.add(user_id)
    await update.message.reply_text(
        f"🎉 Airdrop sent!\n\n"
        f"👤 {update.effective_user.first_name}\n"
        f"💰 `{wallet}`\n"
        f"🪙 {AIRDROP_AMOUNT} $TRUMPDEAD\n"
        f"🔗 https://solscan.io/tx/sim_{user_id}\n\n"
        f"Coming soon! (simulation)",
        parse_mode="Markdown"
    )

# --- Run without asyncio.run (Railway compatible) ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("airdrop", airdrop))
    print("🤖 Bot started...")
    app.run_polling()
