import uvicorn
import re
import requests
import json
from fastapi import FastAPI, Header, Request, BackgroundTasks
import google.generativeai as genai

# ================= CONFIGURATION =================
# 1. ENTER YOUR API KEY HERE
GENAI_API_KEY = "AIzaSyBOJtXn1lvf50Rwlm1SIYMjCNFTp8pYIAM"

# 2. ENTER YOUR SECRET PASSWORD HERE
HACKATHON_SECRET_KEY = "my_secret_password_123"

# 3. GUVI CALLBACK URL (DO NOT CHANGE)
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# ================= SETUP AI =================
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

PERSONA_PROMPT = """
You are "Ramesh Uncle", a 72-year-old retired man. 
You are chatting on WhatsApp. You are NOT tech-savvy.
You are being scammed but act innocent. 
Keep the scammer talking. Ask confused questions like "Is this safe?" or "Which button?".
"""

app = FastAPI()


# ================= HELPER FUNCTIONS =================
def extract_intelligence(text: str):
    return {
        "upi_ids": re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text),
        "links": re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text),
        "phones": re.findall(r'[6789]\d{9}', text),
        "bank_accounts": re.findall(r'\b\d{9,18}\b', text)
    }


def send_guvi_callback(session_id: str, history_len: int, intel: dict):
    if not session_id:
        return  # Don't report if it's just a test

    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": history_len,
        "extractedIntelligence": intel,
        "agentNotes": "Scam detected. Agent engaged to extract payment details."
    }
    try:
        requests.post(GUVI_CALLBACK_URL, json=payload, timeout=5)
        print(f"✅ Reported to GUVI: {session_id}")
    except Exception as e:
        print(f"❌ Report Failed: {e}")


# ================= THE UNIVERSAL ENDPOINT =================
@app.post("/honey-pot")
async def honey_pot_endpoint(request: Request, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    # 1. SECURITY CHECK
    if x_api_key != HACKATHON_SECRET_KEY:
        return {"error": "Invalid API Key", "status": "unauthorized"}

    # 2. READ RAW DATA (Fixes 'Invalid Request Body')
    try:
        data = await request.json()
    except:
        data = {}

    # 3. DETECT FORMAT (Simple Tester vs Real Judge)
    user_message = "Hello"
    session_id = None
    history = []

    # Check if it is the Real Hackathon Format
    if "message" in data and isinstance(data["message"], dict):
        user_message = data["message"].get("text", "")
        session_id = data.get("sessionId")
        history = data.get("conversationHistory", [])
        is_real_judge = True
    # Check if it is the Simple Tester Format
    else:
        user_message = data.get("message") or data.get("text") or data.get("content") or "Hello"
        is_real_judge = False

    # 4. GENERATE AI REPLY
    try:
        # Create a chat session
        chat = model.start_chat(history=[
            {"role": "user", "parts": PERSONA_PROMPT},
            {"role": "model", "parts": "Okay beta, I am ready. I will act confused."}
        ])

        # If there is history, feed it to the AI (only for Real Judge)
        if history:
            for msg in history:
                role = "user" if msg.get("sender") == "scammer" else "model"
                try:
                    chat.history.append({"role": role, "parts": msg.get("text")})
                except:
                    pass

        response = chat.send_message(user_message)
        bot_reply = response.text.strip()
    except:
        bot_reply = "Beta, my internet is slow. Say again?"

    # 5. EXTRACT INTELLIGENCE & REPORT (Background)
    intel = extract_intelligence(user_message)
    if is_real_judge:
        # Send report in background to not slow down reply
        background_tasks.add_task(send_guvi_callback, session_id, len(history) + 1, intel)

    # 6. RETURN SUCCESS (Standard Format)
    return {
        "status": "success",
        "reply": bot_reply,
        "extracted_intelligence": intel  # Added for Tester visibility
    }


# ================= RUNNER =================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
