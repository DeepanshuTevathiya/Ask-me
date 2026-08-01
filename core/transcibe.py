import os
import whisper
import requests
from rich import print
from sarvamai import SarvamAI
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_MODEL = "saaras:v3"
SARVAM_PIECE_SECONDS = 25

_model = None

def load_model():
    global _model

    if _model is None:
        print("LOADING MODEL...")
        _model = whisper.load_model(WHISPER_MODEL)
        print("MODEL SUCCESSFULLY LOADED...")
    return _model

def transcribe_chunk_whisper(chunk_path:str)->str:
    model = load_model()
    result = model.transcribe(chunk_path, task="transcribe")
    return result['text']

def _send_to_sarvam(chunk_path:str)->str:
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    if not os.path.isfile(chunk_path):
        raise FileNotFoundError(f"Audio chunk not found: {chunk_path}")

    headers = {"api-subscription-key": SARVAM_API_KEY}
    data = {"model": SARVAM_MODEL, "with_diarization": "false", "mode": "translate"}

    with open(chunk_path, "rb") as f:
        files = {"file": (os.path.basename(chunk_path), f, "audio/wav")}
        try:
            response = requests.post(
                SARVAM_STT_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=60,
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Sarvam API request failed: {e}") from e

    if not response.ok:
        raise RuntimeError(
            f"Sarvam STT failed [{response.status_code}]: {response.text}"
        )

    return response.json().get("transcript", "")

def transcribe_chunk_saravm(chunk_path:str)->str:
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    try:
        audio = AudioSegment.from_wav(chunk_path)
        piece_ms = SARVAM_PIECE_SECONDS * 1000

        full_text = ""
        total_pieces = (len(audio) + piece_ms - 1) // piece_ms

        for i, start in enumerate(range(0, len(audio), piece_ms)):
            piece = audio[start: start + piece_ms]
            piece_path = f"{chunk_path}_sv_{i}.wav"
            piece.export(piece_path, format="wav")

            try:
                print(f"  → Sarvam piece {i + 1}/{total_pieces} ...")
                full_text += _send_to_sarvam(piece_path) + " "
            finally:
                if os.path.exists(piece_path):
                    os.remove(piece_path)

        return full_text.strip()
    except Exception as e:
        print("Got an error! {e}")

def transcribe_chunk(chunk_path:str, language="english"):
    if language.lower == "hinglish":
        return transcribe_chunk_saravm(chunk_path)
    return transcribe_chunk_whisper(chunk_path)


def transcribe_all(chunks:list, language:str="english")->str:
    full_transcript = ""

    engin = "Sarvam Ai" if language=="hinglish" else "Whisper"
    print(f"'{engin}' IS WORKING...")

    for i, chunk in enumerate(chunks):
        print(f"TRANSCRIBING CHUNK '{i+1}'")
        trascript = transcribe_chunk(chunk, language)

        full_transcript += trascript + " "

    print("TRANSCRIPTION COMPLETE 🎉")
    return full_transcript.strip()
