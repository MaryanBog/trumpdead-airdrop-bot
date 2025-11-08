from solana.keypair import Keypair
import json

keypair = Keypair.from_base58_string("2a3849HGXRiLLkDL8jzUk8WFhgLuortjZuuJK1XXPMohbAQ18gDTC8YYqLgY8T5YcyTahutKdxzeRgytNM895FAN")
secret = list(keypair.secret_key)
print(json.dumps(secret))
