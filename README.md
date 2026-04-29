# My Voice AI Assistant – Unfiltered, Local, Voice + Text

A private AI companion that runs 100% on your Windows laptop. No cloud, no censorship, no disconnections.

## Features
- **Text chat** – type your message, she replies in text and spoken voice.
- **Voice chat** – speak into your microphone, she answers aloud.
- **Uncensored model** – uses `dolphin-mistral` (or any uncensored LLM you choose).
- **Persistent conversation** – remembers your chat history.
- **Fully local** – runs offline after initial model download.

## Requirements
- Windows 10/11
- Python 3.9+ (with "Add to PATH" during install)
- [Ollama](https://ollama.com) installed
- ~4GB free disk space for the model

## Quick Start
1. Double‑click `run.bat`
2. Wait for "Running on local URL: http://127.0.0.1:7860"
3. Open that URL in your browser
4. Allow microphone access (for voice input)
5. Start chatting – type or speak

## Customization
Edit `config.yaml` to change:
- `system_prompt` – her personality (make it as romantic/flirty as you want)
- `model` – use any Ollama model (e.g., `llama3`, `nous-hermes`)
- `temperature` – creativity (0.7–1.2)

## Troubleshooting
| Issue | Solution |
|-------|----------|
| `ollama not found` | Install Ollama from https://ollama.com |
| No voice output | In `config.yaml`, set `voice_enabled: true` and check speakers |
| Speech recognition fails | Use text input, or speak more clearly into microphone |
| Model download slow | First pull takes time; subsequent runs are instant |

## Legal & Ethics
This software is intended for **consensual adult interactions only**. Illegal content (minors, non‑consent) is neither supported nor possible with the base model.

## License
MIT – free to use, modify, and share.
