import requests
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL_ID")

print(f"Token: {TOKEN[:15]}...")
print(f"Canal: {CHANNEL}")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

payload = {
    "chat_id": CHANNEL,
    "text": "✅ ¡Prueba exitosa! El bot funciona correctamente.",
    "parse_mode": "HTML"
}

response = requests.post(url, json=payload)
result = response.json()

if result.get("ok"):
    print("\n✅ Mensaje enviado al canal correctamente")
else:
    print(f"\n❌ Error: {result}")
    print("\nPosibles causas:")
    print("  1. El TOKEN es incorrecto")
    print("  2. El CHANNEL_ID es incorrecto")
    print("  3. El bot no es administrador del canal")