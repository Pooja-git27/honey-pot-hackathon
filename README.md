# 🛡️ AI Agentic Honeypot (Team Ramesh)

### 🚀 Project Overview
This project is an intelligent **AI-powered Honeypot** designed to waste scammers' time and extract their details. It uses a custom persona ("Ramesh Uncle") to engage scammers in realistic, confused conversations while silently capturing their payment details.

### 🌟 Key Features
* **AI Persona:** Powered by Google Gemini 1.5 Flash. Acts as an elderly, non-tech-savvy victim.
* **Live Intel Extraction:** Automatically detects UPI IDs, Phone Numbers, and Bank Accounts using Regex.
* **Real-time Reporting:** Instantly sends detected scam data to the GUVI Hackathon API.
* **Universal Deployment:** Built with FastAPI and deployed on Render Cloud for 24/7 availability.

### 🛠️ Tech Stack
* **Language:** Python 3.10
* **Framework:** FastAPI + Uvicorn
* **AI Model:** Google Gemini 1.5 Flash
* **Deployment:** Render / Ngrok

### ⚡ How to Run
1.  Clone the repo.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run server: `uvicorn main:app --host 0.0.0.0 --port 8000`
