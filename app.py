from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

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
            timeout=15
        )
        data = response.json()
        reply = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Groq error: {e}")
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
