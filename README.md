# Flask Twilio Voicebot

A Flask-based voice bot that integrates Twilio for voice calls, AssemblyAI for transcription, and OpenAI for generating AI-driven responses.

---

## Features
- Receive and process voice calls via Twilio.
- Transcribe audio using AssemblyAI.
- Generate responses using OpenAI GPT.
- Convert responses to speech using pyttsx3.

---

## Prerequisites
- Python 3.8 or higher
- API keys for:
  - [Twilio](https://www.twilio.com/)
  - [AssemblyAI](https://www.assemblyai.com/)
  - [OpenAI](https://platform.openai.com/)

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/flask-twilio-voicebot.git
cd flask-twilio-voicebot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up API Keys
Create a `.env` file in the project directory and add:
```
ASSEMBLYAI_API_KEY=your-assemblyai-api-key
OPENAI_API_KEY=your-openai-api-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
```

### 4. Run the Application
```bash
python app.py
```

### 5. Use with Twilio Webhook
Configure your Twilio webhook to point to:
```
https://<your-server-domain>/handle_call
```

---

## License
MIT License
