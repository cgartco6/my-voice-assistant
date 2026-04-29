import speech_recognition as sr
import pyttsx3
import threading

# Global TTS engine (initialized once)
tts_engine = None

def get_tts_engine():
    global tts_engine
    if tts_engine is None:
        tts_engine = pyttsx3.init()
        rate = tts_engine.getProperty('rate')
        tts_engine.setProperty('rate', 150)
        voices = tts_engine.getProperty('voices')
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                tts_engine.setProperty('voice', voice.id)
                break
    return tts_engine

def speak_text(text):
    """Speak the given text aloud (non-blocking)."""
    engine = get_tts_engine()
    def _speak():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

def transcribe_audio(audio_file_path):
    """Convert audio file (WAV) to text using Google Speech Recognition."""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return "[Could not understand audio]"
    except sr.RequestError:
        return "[Speech recognition service error]"
    except Exception as e:
        return f"[Error: {e}]"
