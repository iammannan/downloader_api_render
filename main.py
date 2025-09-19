from fastapi import FastAPI, Request
import requests, os, re, subprocess, json, tempfile

app = FastAPI()

# ⚠️ Replace this with your bot token directly
BOT_TOKEN = "7583557362:AAHKdmCRcISo2T_RgR2qFMjeO9flr1OiLV0"
URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.get("/")
def home():
    return {"status": "Bot running on Railway ✅"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text:
            # find URLs in the text
            urls = re.findall(r"(https?://\S+)", text)
            if urls:
                reply_texts = []
                for url in urls:
                    try:
                        # Run yt-dlp to get direct media link
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmpfile:
                            subprocess.run(
                                ["yt-dlp", "-j", url],
                                stdout=tmpfile,
                                stderr=subprocess.PIPE,
                                text=True,
                                timeout=30
                            )
                            tmpfile.flush()
                            tmpfile.seek(0)
                            result = json.load(open(tmpfile.name))

                        if "url" in result:
                            reply_texts.append(f"🎬 {url}\n👉 {result['url']}")
                        else:
                            reply_texts.append(f"⚠️ Could not extract: {url}")
                    except Exception as e:
                        reply_texts.append(f"❌ Error extracting {url}: {str(e)}")

                reply = "\n\n".join(reply_texts)
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": reply})
            else:
                # no URL, just echo
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": text})

    return {"ok": True}