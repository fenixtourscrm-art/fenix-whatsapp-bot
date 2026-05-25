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
    print(f"MSG: {incoming_msg} | KEY EXISTS: {bool(GROQ_API_KEY)}")

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
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
        print(f"GROQ STATUS: {response.status_code}")
        print(f"GROQ RESPONSE: {response.text[:300]}")
        data = response.json()
        reply = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"ERROR: {e}")
        reply = f"Debug: {str(e)[:100]}"

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

@app.route("/", methods=["GET"])
def home():
    key_status = "SET" if GROQ_API_KEY else "MISSING"
    return f"Fenix Tours Bot running ✅ | GROQ_API_KEY: {key_status}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
