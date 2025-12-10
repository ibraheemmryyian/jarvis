import os
import sys
import queue
import sounddevice as sd
import json
import subprocess
import requests
import asyncio
import soundfile as sf
from kokoro_onnx import Kokoro
from vosk import Model, KaldiRecognizer
from scipy.io.wavfile import write
from langdetect import detect

# --- Configuration ---
WAKE_WORDS = ["hey jarvis", "hey bitch", "hey gay boy"]
GRAMMAR = '["hey jarvis", "hey bitch", "hey gay boy", "jarvis", "[unk]"]'

# Files
VOSK_MODEL_PATH = "model"
WHISPER_CLI_PATH = "whisper-cli.exe"
WHISPER_MODEL_PATH = "ggml-base.bin"
COMMAND_AUDIO_FILE = "command.wav"
KOKORO_MODEL = "kokoro-v0_19.onnx"
KOKORO_VOICES = "voices.json"

# Brain
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

# Voice Selection
# af_bella is a high quality American Female voice
DEFAULT_VOICE = "af_bella" 

# --- Setup ---
if not os.path.exists(VOSK_MODEL_PATH):
    print(f"[Error] Vosk model not found at '{VOSK_MODEL_PATH}'")
    sys.exit(1)
if not os.path.exists(KOKORO_MODEL):
    print(f"[Error] Kokoro model '{KOKORO_MODEL}' not found. Please download it.")
    sys.exit(1)

print(f"[System] Loading Vosk & Kokoro...")
try:
    # Load Vosk
    model = Model(VOSK_MODEL_PATH)
    rec = KaldiRecognizer(model, 16000, GRAMMAR)
    
    # Load Kokoro Offline TTS
    kokoro = Kokoro(KOKORO_MODEL, KOKORO_VOICES)
except Exception as e:
    print(f"[Error] Load failed: {e}")
    sys.exit(1)

q = queue.Queue()

def callback(indata, frames, time, status):
    if status: print(status, file=sys.stderr)
    q.put(bytes(indata))

# --- Functions ---

def speak(text):
    """Generates and plays offline speech using Kokoro with Language Detection"""
    if not text: return
    print(f"--> 🗣️ Generating Speech...")
    
    # Simple language detection
    try:
        detected_lang = detect(text)
    except:
        detected_lang = "en"

    # Map to Kokoro codes: 'a' (American English), 'f' (French)
    # Default to American English ('a')
    lang_code = 'a'
    if detected_lang == 'fr':
        lang_code = 'f'
        print(f"    [Lang: French detected]")
    else:
        print(f"    [Lang: English detected]")

    try:
        # Generate audio
        # We use the same voice (af_bella) but switch the phoneme language
        samples, sample_rate = kokoro.create(text, voice=DEFAULT_VOICE, speed=1.0, lang=lang_code)
        
        # Play directly using sounddevice
        sd.play(samples, sample_rate)
        sd.wait()
    except Exception as e:
        print(f"[Error] TTS failed: {e}")

def record_command(duration=5):
    print("--> 🎤 Listening for command...")
    fs = 16000
    try:
        myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        write(COMMAND_AUDIO_FILE, fs, myrecording)
        print("--> 🛑 Processing...")
    except Exception as e:
        print(f"[Error] Recording failed: {e}")

def transcribe_command():
    if not os.path.exists(WHISPER_CLI_PATH):
        print("[Error] Whisper CLI not found.")
        return ""
    
    # Whisper handles language detection automatically without -l flag
    cmd = [WHISPER_CLI_PATH, "-m", WHISPER_MODEL_PATH, "-f", COMMAND_AUDIO_FILE, "-nt"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        text = result.stdout.strip()
        print(f"--> You said: {text}")
        return text
    except Exception as e:
        print(f"[Error] Transcription failed: {e}")
        return ""

def get_brain_response(user_input):
    if not user_input: return ""
    
    payload = {
        "messages": [
            {"role": "system", "content": "You are Jarvis. You are helpful, concise, and bilingual. If the user speaks French, reply in French. If English, reply in English."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(LM_STUDIO_URL, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            ai_text = response.json()['choices'][0]['message']['content']
            print(f"\n🤖 JARVIS: {ai_text}\n")
            return ai_text
        else:
            print("[Error] LM Studio returned error.")
            return ""
    except:
        print("[Error] Could not connect to LM Studio.")
        return ""

def listen_for_wake():
    print(f"\n[System] Waiting for: {WAKE_WORDS}")
    
    with sd.RawInputStream(samplerate=16000, blocksize=8000, device=None, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                
                for trigger in WAKE_WORDS:
                    if trigger in text:
                        print(f"\n[!!!] WAKE WORD DETECTED: '{trigger}'")
                        return True

if __name__ == "__main__":
    try:
        while True:
            if listen_for_wake():
                record_command(duration=4) 
                user_text = transcribe_command()
                ai_response = get_brain_response(user_text)
                speak(ai_response)
                
                print("--> Resetting...")
                rec.Reset()
                q.queue.clear()
                
    except KeyboardInterrupt:
        print("\n[System] Stopping...")