from fastapi import FastAPI, Request
import requests, re

app = FastAPI()

# ⚠️ Replace this with your bot token directly
BOT_TOKEN2 = "7342710360:AAG6RlHdN371oNdLhT5_MlplEvZKXxQ90Mc"
URL = f"https://api.telegram.org/bot{BOT_TOKEN2}"

@app.get("/")
def home():
    return {"status": "Bot running on Railway ✅"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    # Handle /start
    if text == "/start":
        reply = "👋 Hi! Send me any link and I’ll reply with it."
        requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": reply})
        return {"ok": True}

    # Echo back links (basic demo)
    urls = re.findall(r"(https?://\S+)", text)
    if urls:
        reply = "🔗 I found these links:\n" + "\n".join
