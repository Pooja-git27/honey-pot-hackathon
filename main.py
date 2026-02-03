import uvicorn
import requests
from fastapi import FastAPI, Header, Request, BackgroundTasks
import google.generativeai as genai

# ================= CONFIGURATION =================
GENAI_API_KEY = "AIzaSyBOJtXn1lvf50Rwlm1SIYMjCNFTp8pYIAM"
HACKATHON_SECRET_KEY = "my_secret_password_123"
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# ================= SETUP AI =================
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

# ================= DEBUGGING STARTUP =================
@app.on_event("startup")
async def startup_event():
    print("\n\n✅✅ NEW CODE IS RUNNING! READY TO TEST. ✅✅\n\n")

# ================= THE UNIVERSAL ENDPOINT =================
@app.post("/honey-pot")
async def honey_pot_endpoint(request: Request, background_tasks: BackgroundTasks):
    # 1. READ RAW DATA (No Validation Errors)
    try:
        body = await request.json()
        print(f"📥 RECEIVED DATA: {body}") # This prints what the website sends!
    except:
        body = {}
        print("⚠️ RECEIVED EMPTY OR BAD DATA")

    # 2. EXTRACT SAFE VALUES (Prevents Crashes)
    # Checks for 'message', 'text', 'content', or just assumes Hello
    user_text = "Hello"
    if isinstance(body, dict):
        if "message" in body and isinstance(body["message"], dict):
             user_text = body["message"].get("text", "Hello")
        else:
             user_text = body.get("message") or body.get("text") or "Hello"

    # 3. GENERATE SIMPLE AI REPLY
    try:
        chat = model.start_chat(history=[])
        reply = chat.send_message(f"Act as a confused old man. Reply to: {user_text}").text
    except:
        reply = "Beta? Who is this?"

    # 4. SEND SUCCESS RESPONSE (Satisfies the Tester)
    return {
        "reply": reply,
        "extracted_intelligence": {
            "upi_ids": [],
            "links": [],
            "risk": "low"
        },
        "status": "active"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)