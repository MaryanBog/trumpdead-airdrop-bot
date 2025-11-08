from solana.keypair import Keypair
import json

base58_key = "2a3849HGXRiLLkDL8jzUk8WFhgLuortjZuuJK1XXPMohbAQ18gDTC8YYqLgY8T5YcyTahutKdxzeRgytNM895FAN"
keypair = Keypair.from_base58_string(base58_key)
secret_array = list(keypair.secret_key)
print(json.dumps(secret_array))
