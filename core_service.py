import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solana.rpc.providers.http import HTTPProvider
from spl.token.instructions import transfer_checked, get_associated_token_address
from spl.token.constants import TOKEN_PROGRAM_ID

# --- ENV ---
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY is missing")

# --- Token config ---
TOKEN_MINT = Pubkey.from_string("CLX3PRe79QGUzKT1ZwNA5nVcPb4SEGoqJD5oTwJMpump")
TOKEN_DECIMALS = 6
AMOUNT_TO_SEND = 100 * (10 ** TOKEN_DECIMALS)

# --- RPC ---
client = HTTPProvider("https://api.mainnet-beta.solana.com")
sender = Keypair.from_base58_string(PRIVATE_KEY)

# --- FastAPI ---
app = FastAPI()

class AirdropRequest(BaseModel):
    wallet: str
    user_id: int

@app.post("/airdrop")
def airdrop(req: AirdropRequest):
    try:
        recipient = Pubkey.from_string(req.wallet)
        sender_ata = get_associated_token_address(sender.pubkey(), TOKEN_MINT)
        recipient_ata = get_associated_token_address(recipient, TOKEN_MINT)

        ix = transfer_checked(
            program_id=TOKEN_PROGRAM_ID,
            source=sender_ata,
            mint=TOKEN_MINT,
            dest=recipient_ata,
            owner=sender.pubkey(),
            amount=AMOUNT_TO_SEND,
            decimals=TOKEN_DECIMALS,
            signers=[]
        )

        blockhash = client.get_latest_blockhash()
        tx = Transaction([ix], sender.pubkey(), blockhash.value.blockhash)

        sig = client.send_transaction(tx, sender)
        return {"tx_signature": str(sig)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
