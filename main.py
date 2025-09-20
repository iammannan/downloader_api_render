from fastapi import FastAPI, Request
import requests, re, subprocess, json, tempfile

app = FastAPI()

# ⚠️ Replace this with your bot token directly
BOT_TOKEN = "7583557362:AAHKdmCRcISo2T_RgR2qFMjeO9flr1OiLV0"
URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Browser name for yt-dlp cookies (chrome, edge, brave, firefox, opera, etc.)
BROWSER = "chrome"


@app.get("/")
def home():
    return {"status": "Bot running with yt-dlp ✅"}


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
                        # temp file for JSON output
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmpfile:
                            cmd = ["yt-dlp", "-j", "--cookies", "biscuit.txt", url]

                            # Add cookies-from-browser
                            cmd.extend(["--cookies-from-browser", BROWSER])

                            proc = subprocess.run(
                                cmd,
                                stdout=tmpfile,
                                stderr=subprocess.PIPE,
                                text=True,
                                timeout=30
                            )

                            if proc.returncode != 0:
                                # yt-dlp failed → return errors
                                error_msg = proc.stderr.strip().split("\n")[-1]
                                reply_texts.append(f"❌ {url}\nError: {error_msg}")
                                continue

                            tmpfile.flush()
                            tmpfile.seek(0)
                            result = json.load(open(tmpfile.name))

                        if "url" in result:
                            reply_texts.append(f"🎬 {url}\n👉 {result['url']}")
                        else:
                            reply_texts.append(f"⚠️ Could not extract media from: {url}")

                    except Exception as e:
                        reply_texts.append(f"❌ {url}\nException: {str(e)}")


                reply = "\n\n".join(reply_texts)
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": reply})
            else:
                # no URL, just echo
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": text})

    return {"ok": True}
