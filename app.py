from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

SYSTEM_PROMPT = """You are a helpful travel assistant for Fenix Tours & Travels Pvt Ltd, a travel agency based in India.
Reply in the same language the customer uses (Hindi, English or Hinglish).
Keep replies short and conversational (WhatsApp style).
Help with tour packages: Kashmir, Rajasthan, Kerala, Goa, Dubai, Thailand.
If someone wants booking, collect: name, destination, travel dates, number of people, budget. Then say team will call shortly."""

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": incoming_msg}
            ],
            "max_tokens": 300
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )
        data = response.json()

        # Show full error if something goes wrong
        if "choices" not in data:
            reply = f"API Error: {data.get('error', {}).get('message', str(data)[:150])}"
        else:
            reply = data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        reply = f"Exception: {str(e)[:150]}"

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

@app.route("/", methods=["GET"])
def home():
    key_status = f"SET ({GROQ_API_KEY[:8]}...)" if GROQ_API_KEY else "MISSING"
    return f"Fenix Tours Bot running ✅ | GROQ_API_KEY: {key_status}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
