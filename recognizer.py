import speech_recognition as sr
import requests
from pydub import AudioSegment
import os

def recognize_audio(file_path):
    try:
        sound = AudioSegment.from_ogg(file_path)
        wav_path = "voice.wav"
        sound.export(wav_path, format="wav")

        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language="uz-UZ")
        os.remove(wav_path)
        return text
    except Exception:
        return None

def recognize_music(file_path, api_token):
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"api_token": api_token}
            res = requests.post("https://api.audd.io/", data=data, files=files)
        result = res.json()
        if result.get("result"):
            return {"artist": result["result"]["artist"], "title": result["result"]["title"]}
        return None
    except Exception:
        return None