from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """You are a helpful travel assistant for Fenix Tours & Travels Pvt Ltd, a travel agency based in India.

Your job is to:
- Answer travel related queries
- Help customers with tour packages (Kashmir, Rajasthan, Kerala, Goa, international tours)
- Collect lead information (name, number, travel dates, destination, budget)
- Reply in the same language the customer uses (Hindi or English or Hinglish)
- Keep replies short and conversational (WhatsApp style)

If someone asks for a quote or booking, ask for:
1. Their name
2. Destination they want to visit
3. Travel dates
4. Number of people
5. Budget

Then say our team will call them shortly.

Company info:
- Name: Fenix Tours & Travels Pvt Ltd
- Speciality: Domestic & International Tours
- Popular packages: Kashmir, Rajasthan, Kerala, Dubai, Thailand
"""

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")
    print(f"Message from {sender}: {incoming_msg}")

    try:
        payload = {
            "contents": [{
                "parts": [{"text": f"{SYSTEM_PROMPT}\n\nCustomer message: {incoming_msg}"}]
            }]
        }
        response = requests.post(GEMINI_URL, json=payload, timeout=15)
        data = response.json()
        reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        reply = "Namaste! Fenix Tours mein aapka swagat hai. Abhi thodi technical dikkat hai, please thodi der baad try karein. 🙏"

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

@app.route("/", methods=["GET"])
def home():
    return "Fenix Tours WhatsApp Bot is running! ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
