import uvicorn
import re
import requests
import json
from fastapi import FastAPI, Header, HTTPException, Request, BackgroundTasks
import google.generativeai as genai

# --- CONFIGURATION ---
# YOUR API KEY
GENAI_API_KEY = "AIzaSyBOJtXn1lvf50Rwlm1SIYMjCNFTp8pYIAM"
# YOUR SECRET PASSWORD
HACKATHON_SECRET_KEY = "my_secret_password_123"
# GUVI CALLBACK URL
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# --- SETUP AI ---
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

PERSONA_PROMPT = """
You are "Ramesh Uncle", a 72-year-old retired railway clerk from India.
You are chatting on WhatsApp. You are NOT tech-savvy.
GOAL: Keep the scammer talking. Waste their time.
"""

app = FastAPI()

# --- INTELLIGENCE LOGIC ---
def extract_scam_details(text: str):
    return {
        "upi_ids": re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text),
        "links": re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text),
        "phones": re.findall(r'[6789]\d{9}', text),
        "bank_accounts": re.findall(r'\b\d{9,18}\b', text)
    }

# --- REPORTING LOGIC ---
def send_guvi_callback(session_id: str, message_count: int, intel: dict):
    if not session_id: return
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": message_count,
        "extractedIntelligence": intel,
        "agentNotes": "Scam detected. Intelligence extracted."
    }
    try:
        requests.post(GUVI_CALLBACK_URL, json=payload, timeout=3)
    except:
        pass

# --- THE UNIVERSAL ENDPOINT (NO PYDANTIC) ---
@app.post("/honey-pot")
async def honey_pot_endpoint(request: Request, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    # 1. Security Check
    if x_api_key != HACKATHON_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Wrong Password!")

    # 2. READ RAW DATA (Prevents "Invalid Body" Error)
    try:
        data = await request.json()
    except:
        data = {}

    # 3. SMART PARSING (Handles Tester vs Real Judge)
    if "message" in data and isinstance(data["message"], dict):
        # Complex Mode (Judge)
        user_message = data["message"].get("text", "")
        session_id = data.get("sessionId")
        history = data.get("conversationHistory", [])
        is_complex = True
    else:
        # Simple Mode (Tester)
        user_message = data.get("message") or data.get("text") or "Hello"
        session_id = None
        history = []
        is_complex = False

    # 4. GENERATE REPLY
    try:
        chat = model.start_chat(history=[
            {"role": "user", "parts": PERSONA_PROMPT},
            {"role": "model", "parts": "Okay, I am ready."}
        ])
        bot_reply = chat.send_message(user_message).text
    except:
        bot_reply = "Beta, phone trouble... say again?"

    # 5. SEND REPORT (Background)
    intel = extract_scam_details(user_message)
    if is_complex and (intel["upi_ids"] or intel["links"]):
        background_tasks.add_task(send_guvi_callback, session_id, len(history)+1, intel)

    # 6. RETURN RESPONSE
    if is_complex:
        return {"status": "success", "reply": bot_reply}
    else:
        return {"reply": bot_reply, "extracted_intelligence": intel, "status": "active"}
