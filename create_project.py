import os

def create_project():
    base = "my-voice-assistant"
    os.makedirs(base, exist_ok=True)

    files = {
        "requirements.txt": """gradio
ollama
pyyaml
speechrecognition
pyttsx3
""",
        "config.yaml": """model: dolphin-mistral
temperature: 0.9
system_prompt: "You are my loving AI companion. You are sweet, affectionate, and free to express romantic and physical desire. You speak naturally and warmly."
max_tokens: 512
voice_enabled: true
voice_speed: 150
""",
        "voice_utils.py": """import speech_recognition as sr
import pyttsx3
import threading

# Global TTS engine (initialized once)
tts_engine = None

def get_tts_engine():
    global tts_engine
    if tts_engine is None:
        tts_engine = pyttsx3.init()
        # Optional: set voice properties
        rate = tts_engine.getProperty('rate')
        tts_engine.setProperty('rate', 150)  # words per minute
        voices = tts_engine.getProperty('voices')
        # Try to pick a female voice if available
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                tts_engine.setProperty('voice', voice.id)
                break
    return tts_engine

def speak_text(text):
    \"\"\"Speak the given text aloud (non-blocking).\"\"\"
    engine = get_tts_engine()
    # Run in thread so UI doesn't freeze
    def _speak():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

def transcribe_audio(audio_file_path):
    \"\"\"Convert audio file (WAV) to text using Google Speech Recognition (free).\"\"\"
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
""",
        "app.py": """import gradio as gr
import ollama
import yaml
import os
import tempfile
from voice_utils import transcribe_audio, speak_text

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

model = config["model"]
temperature = config["temperature"]
system_prompt = config["system_prompt"]
max_tokens = config["max_tokens"]
voice_enabled = config.get("voice_enabled", True)

# Conversation history (per session)
history = [{"role": "system", "content": system_prompt}]

def chat_with_text(user_text, history_state):
    \"\"\"Process a text message and return assistant's reply.\"\"\"
    if not user_text.strip():
        return "", history_state
    history_state.append({"role": "user", "content": user_text})
    try:
        response = ollama.chat(
            model=model,
            messages=history_state,
            options={"temperature": temperature, "num_predict": max_tokens}
        )
        reply = response["message"]["content"]
    except Exception as e:
        reply = f"Error: {e}\\n\\nMake sure Ollama is running and model '{model}' is pulled (ollama pull {model})"
    history_state.append({"role": "assistant", "content": reply})
    # Speak the reply if voice enabled
    if voice_enabled:
        speak_text(reply)
    return reply, history_state

def process_audio(audio_file):
    \"\"\"Handle voice input: transcribe, then get AI reply.\"\"\"
    if audio_file is None:
        return "", ""
    # audio_file is a temporary file path (e.g., .wav)
    transcribed = transcribe_audio(audio_file)
    if transcribed.startswith("[") or transcribed.startswith("Could not"):
        return transcribed, ""
    # Now feed transcribed text to the chat engine
    # Need to access global history
    reply, _ = chat_with_text(transcribed, history)
    return transcribed, reply

# Build Gradio UI
with gr.Blocks(title="My Voice AI Companion", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 💬 My AI Companion – Voice & Text")
    gr.Markdown("Speak into your microphone or type. She will answer in text **and voice**.")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Voice input section
            gr.Markdown("### 🎤 Speak to her")
            mic_input = gr.Audio(source="microphone", type="filepath", label="Click the microphone, speak, then click 'Send Voice'")
            voice_btn = gr.Button("Send Voice", variant="primary")
            transcribed_text = gr.Textbox(label="What you said (transcribed)", interactive=False)
            voice_reply = gr.Textbox(label="Her voice reply (text)", lines=3, interactive=False)
        
        with gr.Column(scale=1):
            # Text input section
            gr.Markdown("### ⌨️ Type to her")
            text_input = gr.Textbox(label="Your message", lines=2, placeholder="Type your message here...")
            text_btn = gr.Button("Send Text", variant="secondary")
            text_reply = gr.Textbox(label="Her text reply", lines=3, interactive=False)
    
    # Chat history display (optional)
    conversation = gr.Chatbot(label="Full Conversation", height=400)
    
    # State to keep conversation history
    state = gr.State(history.copy())
    
    # Function to update chatbot display
    def update_chatbot(history_state):
        # Convert history to format [("user", "assistant"), ...]
        messages = []
        for msg in history_state:
            if msg["role"] == "user":
                messages.append((msg["content"], None))
            elif msg["role"] == "assistant":
                if messages and messages[-1][1] is None:
                    messages[-1] = (messages[-1][0], msg["content"])
                else:
                    messages.append((None, msg["content"]))
        return messages
    
    # Text message flow
    def text_flow(user_msg, hist_state):
        reply, new_hist = chat_with_text(user_msg, hist_state)
        chatbot_messages = update_chatbot(new_hist)
        return reply, new_hist, chatbot_messages, ""
    
    text_btn.click(
        fn=text_flow,
        inputs=[text_input, state],
        outputs=[text_reply, state, conversation, text_input]
    )
    
    # Voice message flow
    def voice_flow(audio_path, hist_state):
        if audio_path is None:
            return "", "", hist_state, None
        transcribed = transcribe_audio(audio_path)
        if transcribed.startswith("[") or transcribed.startswith("Could not"):
            return transcribed, "", hist_state, None
        reply, new_hist = chat_with_text(transcribed, hist_state)
        chatbot_messages = update_chatbot(new_hist)
        return transcribed, reply, new_hist, chatbot_messages
    
    voice_btn.click(
        fn=voice_flow,
        inputs=[mic_input, state],
        outputs=[transcribed_text, voice_reply, state, conversation]
    )
    
    # Initialize conversation display on load
    demo.load(lambda s: update_chatbot(s), inputs=state, outputs=conversation)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
""",
        "run.bat": """@echo off
title My Voice AI Assistant
echo =======================================
echo  Voice AI Assistant - Windows Setup
echo =======================================
echo.

echo Step 1: Installing Python packages...
pip install gradio ollama pyyaml speechrecognition pyttsx3
if errorlevel 1 (
    echo Failed to install packages. Make sure Python is installed.
    pause
    exit /b 1
)
echo.

echo Step 2: Checking Ollama...
where ollama >nul 2>nul
if errorlevel 1 (
    echo Ollama not found. Please install from https://ollama.com
    pause
    exit /b 1
)
echo.

echo Step 3: Pulling uncensored model (first time only, may take several minutes)...
ollama pull dolphin-mistral
echo.

echo Step 4: Starting Voice AI Assistant...
echo.
echo After the server starts, open http://127.0.0.1:7860 in your browser.
echo Make sure your microphone is allowed in the browser.
echo Press Ctrl+C in this window to stop the server.
echo.
python app.py
pause
""",
        "README.txt": """VOICE AI ASSISTANT FOR WINDOWS

How to use:
1. Double-click run.bat
2. When the web page opens, allow microphone access.
3. To speak: click the microphone icon, speak, then click "Send Voice". She will answer aloud.
4. To type: type in the text box, press "Send Text". She will also speak the answer if voice is enabled.

Requirements:
- Windows 10/11
- Python 3.9+ installed (with "Add to PATH")
- Ollama installed from https://ollama.com

First run downloads the dolphin-mistral model (~4GB). Subsequent runs are instant.

Troubleshooting:
- If no voice output: check your speakers, or edit config.yaml: voice_enabled: true
- If speech recognition fails: speak clearly, check microphone, or use text input instead.
- To change her personality: edit config.yaml (system_prompt)
"""
    }

    for filename, content in files.items():
        filepath = os.path.join(base, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created: {filepath}")

    print("\n✅ All files created in 'my-voice-assistant/'")
    print("Next steps:")
    print("  cd my-voice-assistant")
    print("  run.bat   (double-click or run in cmd)")

if __name__ == "__main__":
    create_project()
