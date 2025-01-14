import os
import requests
import openai
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import pyttsx3
import tempfile
import aiohttp
import asyncio
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file


# Use the environment variables
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def download_audio_file(url):
    """Downloads the audio file from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Save to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        logger.error(f"Error downloading audio file: {e}")
        raise


def compress_audio(file_path):
    """Placeholder for audio compression logic."""
    # You can implement audio compression here if needed, e.g., using ffmpeg.
    return file_path


async def upload_audio_to_assemblyai_async(audio_file_path):
    """Uploads the audio file to AssemblyAI asynchronously."""
    try:
        headers = {'authorization': ASSEMBLYAI_API_KEY}
        upload_url = "https://api.assemblyai.com/v2/upload"

        async with aiohttp.ClientSession() as session:
            with open(audio_file_path, 'rb') as f:
                async with session.post(upload_url, headers=headers, data=f) as response:
                    response.raise_for_status()
                    return (await response.json())['upload_url']
    except Exception as e:
        logger.error(f"Error uploading audio to AssemblyAI: {e}")
        raise


async def request_transcription_async(audio_url):
    """Requests transcription from AssemblyAI asynchronously."""
    try:
        headers = {'authorization': ASSEMBLYAI_API_KEY}
        transcript_url = "https://api.assemblyai.com/v2/transcript"
        data = {"audio_url": audio_url}

        async with aiohttp.ClientSession() as session:
            async with session.post(transcript_url, json=data, headers=headers) as response:
                response.raise_for_status()
                return (await response.json())["id"]
    except Exception as e:
        logger.error(f"Error requesting transcription: {e}")
        raise


async def get_transcription_result_async(transcript_id):
    """Retrieves transcription results from AssemblyAI."""
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    transcript_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(transcript_url, headers=headers) as response:
                response.raise_for_status()
                result = await response.json()

                if result["status"] == "completed":
                    return result["text"]
                elif result["status"] == "failed":
                    logger.error("Transcription failed!")
                    raise RuntimeError("Transcription failed!")

        await asyncio.sleep(1)  # Retry after 1 second


def generate_ai_response(user_text):
    """Generates an AI response using OpenAI GPT."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and polite customer support agent."},
                {"role": "user", "content": user_text},
            ],
            max_tokens=150
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        raise


def text_to_speech(text):
    """Converts text to speech using pyttsx3."""
    try:
        engine = pyttsx3.init()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        engine.save_to_file(text, temp_file.name)
        engine.runAndWait()
        return temp_file.name
    except Exception as e:
        logger.error(f"Error in text-to-speech conversion: {e}")
        raise


async def upload_to_public_server(file_path):
    """Uploads a file to a public server and returns the public URL."""
    # Placeholder for uploading logic. Use AWS S3, Google Cloud, or similar services.
    logger.warning("Public upload function not implemented.")
    raise NotImplementedError("Public upload function not implemented")


async def handle_audio_processing(recording_url):
    """Handles the end-to-end audio processing pipeline."""
    try:
        recording_file = download_audio_file(recording_url)
        compressed_file = compress_audio(recording_file)
        audio_url = await upload_audio_to_assemblyai_async(compressed_file)
        transcript_id = await request_transcription_async(audio_url)
        user_text = await get_transcription_result_async(transcript_id)
        return user_text
    except Exception as e:
        logger.error(f"Error in audio processing pipeline: {e}")
        raise


@app.route("/handle_call", methods=["POST"])
async def handle_call():
    """Handles incoming calls using Twilio."""
    try:
        recording_url = request.form["RecordingUrl"]
        user_text = await handle_audio_processing(recording_url)

        # Generate AI response
        ai_response = generate_ai_response(user_text)

        # Convert AI response to speech
        speech_file = text_to_speech(ai_response)

        # Upload the speech file to a public server
        public_audio_url = await upload_to_public_server(speech_file)

        # Twilio response
        response = VoiceResponse()
        response.play(public_audio_url)
        return str(response)
    except Exception as e:
        logger.error(f"Error handling call: {e}")
        return str(e), 500


if __name__ == "__main__":
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:5000"]
    asyncio.run(serve(app, config))
