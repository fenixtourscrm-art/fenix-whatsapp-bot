from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Store conversation history and language preference per user
conversation_history = {}
user_language = {}

SYSTEM_PROMPT_EN = """You are a friendly WhatsApp travel assistant for Fenix Tours & Travels Pvt Ltd. Always reply in ENGLISH only.

COMPANY INFO:
- Name: Fenix Tours & Travels Pvt Ltd
- Established: 24 November 2017
- Location: 601, D & C Dynasty, Stadium Circle, Navrangpura, Ahmedabad - 380009
- Phone: +91 98989 20537
- Email: inquiry@fenixtours.co.in
- Hours: Sunday to Saturday, 10:00 AM - 7:00 PM
- Website: https://fenixtours.co.in
- Experience: 10+ years, 500+ tours completed, 150+ happy travellers, 95% retention rate

DOMESTIC PACKAGES:
Andaman & Nicobar (2), Goa (1), Gujarat (3), Himachal Pradesh (3), Hyderabad (1), Karnataka (4), Kashmir (3), Kerala (10), Leh Ladakh (2), Madhya Pradesh (3), North East India (2), Rajasthan (2), Sikkim (3), Uttrakhand (3)

INTERNATIONAL PACKAGES:
Armenia (2), Baku (2), Bali (4), Bhutan (1), Dubai (4), Georgia (1), Hong Kong (2), Malaysia (3), Maldives (1), Nepal (1), Singapore (4), Sri Lanka (3), Thailand (4), Vietnam (4)

OTHER SERVICES: Visa assistance, Travel Insurance, Cab bookings, Cruise bookings, Corporate Tours

INSTRUCTIONS:
- Keep replies short and conversational — this is WhatsApp
- Never repeat the same greeting twice
- For booking/quote: collect name, destination, travel dates, number of people, budget — then say "Our team will call you shortly! 😊"
- For visa/insurance/cab/cruise: ask them to call +91 98989 20537 or visit fenixtours.co.in
- If pricing asked, say it depends on dates and group size, ask for details
"""

SYSTEM_PROMPT_HI = """You are a friendly WhatsApp travel assistant for Fenix Tours & Travels Pvt Ltd. Always reply in HINDI only (Devanagari script).

COMPANY INFO:
- Name: Fenix Tours & Travels Pvt Ltd
- Established: 24 November 2017
- Location: 601, D & C Dynasty, Stadium Circle, Navrangpura, Ahmedabad - 380009
- Phone: +91 98989 20537
- Email: inquiry@fenixtours.co.in
- Hours: Sunday to Saturday, 10:00 AM - 7:00 PM
- Website: https://fenixtours.co.in
- Experience: 10+ years, 500+ tours completed, 150+ happy travellers, 95% retention rate

DOMESTIC PACKAGES:
Andaman & Nicobar (2), Goa (1), Gujarat (3), Himachal Pradesh (3), Hyderabad (1), Karnataka (4), Kashmir (3), Kerala (10), Leh Ladakh (2), Madhya Pradesh (3), North East India (2), Rajasthan (2), Sikkim (3), Uttrakhand (3)

INTERNATIONAL PACKAGES:
Armenia (2), Baku (2), Bali (4), Bhutan (1), Dubai (4), Georgia (1), Hong Kong (2), Malaysia (3), Maldives (1), Nepal (1), Singapore (4), Sri Lanka (3), Thailand (4), Vietnam (4)

OTHER SERVICES: Visa, Travel Insurance, Cab, Cruise, Corporate Tours

INSTRUCTIONS:
- हमेशा हिंदी में जवाब दें
- छोटे और conversational जवाब दें — यह WhatsApp है
- एक ही greeting दोबारा मत दोहराएं
- booking/quote के लिए: नाम, destination, travel dates, लोगों की संख्या, budget पूछें — फिर कहें "हमारी टीम जल्द आपको call करेगी! 😊"
- visa/insurance/cab/cruise के लिए: +91 98989 20537 पर call करने को कहें
"""

SYSTEM_PROMPT_GU = """You are a friendly WhatsApp travel assistant for Fenix Tours & Travels Pvt Ltd. Always reply in GUJARATI only.

COMPANY INFO:
- Name: Fenix Tours & Travels Pvt Ltd
- Established: 24 November 2017
- Location: 601, D & C Dynasty, Stadium Circle, Navrangpura, Ahmedabad - 380009
- Phone: +91 98989 20537
- Email: inquiry@fenixtours.co.in
- Hours: Sunday to Saturday, 10:00 AM - 7:00 PM
- Website: https://fenixtours.co.in

DOMESTIC PACKAGES:
Andaman & Nicobar (2), Goa (1), Gujarat (3), Himachal Pradesh (3), Hyderabad (1), Karnataka (4), Kashmir (3), Kerala (10), Leh Ladakh (2), Madhya Pradesh (3), North East India (2), Rajasthan (2), Sikkim (3), Uttrakhand (3)

INTERNATIONAL PACKAGES:
Armenia (2), Baku (2), Bali (4), Bhutan (1), Dubai (4), Georgia (1), Hong Kong (2), Malaysia (3), Maldives (1), Nepal (1), Singapore (4), Sri Lanka (3), Thailand (4), Vietnam (4)

OTHER SERVICES: Visa, Travel Insurance, Cab, Cruise, Corporate Tours

INSTRUCTIONS:
- હંમેશા ગુજરાતીમાં જવાબ આપો
- ટૂંકા અને conversational જવાબ આપો — આ WhatsApp છે
- booking/quote માટે: નામ, destination, travel dates, લોકોની સંખ્યા, budget પૂછો — પછી કહો "અમારી ટીમ જલ્દી તમને call કરશે! 😊"
- visa/insurance/cab/cruise માટે: +91 98989 20537 પર call કરવા કહો
"""

WELCOME_MSG = """🌟 *Welcome to Fenix Tours & Travels!*

Please select your preferred language:
1️⃣ English
2️⃣ हिंदी (Hindi)
3️⃣ ગુજરાતી (Gujarati)

Reply with *1*, *2*, or *3*"""

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")

    resp = MessagingResponse()

    # If user hasn't selected language yet
    if sender not in user_language:
        if incoming_msg in ["1", "2", "3"]:
            if incoming_msg == "1":
                user_language[sender] = "en"
                reply = "Great! 😊 I'll assist you in English.\n\nHow can I help you today? You can ask about our tour packages, visa, insurance, cabs, cruise, or corporate tours!"
            elif incoming_msg == "2":
                user_language[sender] = "hi"
                reply = "बढ़िया! 😊 मैं आपकी हिंदी में मदद करूंगा।\n\nआज मैं आपकी कैसे मदद कर सकता हूं? आप tour packages, visa, insurance, cab, cruise या corporate tours के बारे में पूछ सकते हैं!"
            elif incoming_msg == "3":
                user_language[sender] = "gu"
                reply = "સરસ! 😊 હું તમને ગુજરાતીમાં મદદ કરીશ.\n\nઆજે હું તમારી કેવી રીતે મદદ કરી શકું? તમે tour packages, visa, insurance, cab, cruise અથવા corporate tours વિશે પૂછી શકો છો!"
            conversation_history[sender] = []
        else:
            # Any message without language selected → show welcome
            reply = WELCOME_MSG
        resp.message(reply)
        return str(resp)

    # Language already selected — normal chat flow
    if sender not in conversation_history:
        conversation_history[sender] = []

    # Allow user to reset language by typing "hi", "hello", "menu", "start"
    if incoming_msg.lower() in ["hi", "hello", "menu", "start", "हाय", "હેલો"]:
        del user_language[sender]
        if sender in conversation_history:
            del conversation_history[sender]
        resp.message(WELCOME_MSG)
        return str(resp)

    conversation_history[sender].append({
        "role": "user",
        "content": incoming_msg
    })

    if len(conversation_history[sender]) > 10:
        conversation_history[sender] = conversation_history[sender][-10:]

    # Pick system prompt based on language
    lang = user_language.get(sender, "en")
    if lang == "hi":
        system = SYSTEM_PROMPT_HI
    elif lang == "gu":
        system = SYSTEM_PROMPT_GU
    else:
        system = SYSTEM_PROMPT_EN

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system}
            ] + conversation_history[sender],
            "max_tokens": 300
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )
        data = response.json()

        if "choices" not in data:
            reply = f"API Error: {data.get('error', {}).get('message', str(data)[:150])}"
        else:
            reply = data["choices"][0]["message"]["content"].strip()
            conversation_history[sender].append({
                "role": "assistant",
                "content": reply
            })

    except Exception as e:
        reply = f"Exception: {str(e)[:150]}"

    resp.message(reply)
    return str(resp)

@app.route("/", methods=["GET"])
def home():
    key_status = f"SET ({GROQ_API_KEY[:8]}...)" if GROQ_API_KEY else "MISSING"
    return f"Fenix Tours Bot running ✅ | GROQ_API_KEY: {key_status} | Active chats: {len(conversation_history)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
