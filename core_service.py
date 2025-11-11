import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.instruction import Instruction, AccountMeta
from solders.message import Message
from solana.rpc.api import Client
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address

# --- Logging ---
logging.basicConfig(level=logging.INFO)
print("✅ Starting FastAPI initialization...")

# --- ENV ---
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("❌ PRIVATE_KEY is missing")

try:
    print("Loading PRIVATE_KEY...")
    PRIVATE_KEY = PRIVATE_KEY.strip()
    print("PRIVATE_KEY length:", len(PRIVATE_KEY))
    sender = Keypair.from_base58_string(PRIVATE_KEY)
    print("✅ Keypair loaded successfully")
except Exception as e:
    print("❌ Error loading keypair:", e)
    raise

# --- Token config ---
TOKEN_MINT = Pubkey.from_string("CLX3PRe79QGUzKT1ZwNA5nVcPb4SEGoqJD5oTwJMpump")
TOKEN_DECIMALS = 6
AMOUNT_TO_SEND = 100 * (10 ** TOKEN_DECIMALS)

# --- RPC ---
RPC_URL = os.getenv("RPC_URL", "https://api.mainnet-beta.solana.com")
print(f"Using RPC: {RPC_URL}")
client = Client(RPC_URL)

# --- FastAPI App ---
app = FastAPI()

class AirdropRequest(BaseModel):
    wallet: str
    user_id: int

@app.get("/")
def root():
    return {"status": "ok", "message": "TrumpDead Airdrop API is live!"}

@app.post("/airdrop")
def airdrop(req: AirdropRequest):
    try:
        print(f"Received airdrop request for wallet: {req.wallet}")
        recipient = Pubkey.from_string(req.wallet)
        sender_ata = get_associated_token_address(sender.pubkey(), TOKEN_MINT)
        recipient_ata = get_associated_token_address(recipient, TOKEN_MINT)

        # --- Сборка TransferChecked вручную ---
        data = bytes([
            12,  # TransferChecked instruction index
            *AMOUNT_TO_SEND.to_bytes(8, "little"),  # amount: u64
            TOKEN_DECIMALS  # decimals: u8
        ])

        accounts = [
            AccountMeta(pubkey=sender_ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=TOKEN_MINT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=recipient_ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=sender.pubkey(), is_signer=True, is_writable=False),
        ]

        ix = Instruction(program_id=TOKEN_PROGRAM_ID, accounts=accounts, data=data)

        # --- Формируем Message и Transaction ---
        message = Message([ix], payer=sender.pubkey())
        tx = Transaction(message, [sender])

        # --- Получаем актуальный блокхеш ---
        blockhash_resp = client.get_latest_blockhash()
        blockhash = blockhash_resp.value.blockhash

        tx.recent_blockhash = blockhash

        # --- Отправляем транзакцию ---
        sig = client.send_transaction(tx, sender)
        print(f"✅ Airdrop sent successfully! Signature: {sig}")
        return {"tx_signature": str(sig)}

    except Exception as e:
        logging.error(f"Airdrop error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Run for local testing / Railway ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("core_service:app", host="0.0.0.0", port=port)
