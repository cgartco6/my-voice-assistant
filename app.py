import gradio as gr
import ollama
import yaml
import os
from voice_utils import transcribe_audio, speak_text

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

model = config["model"]
temperature = config["temperature"]
system_prompt = config["system_prompt"]
max_tokens = config["max_tokens"]
voice_enabled = config.get("voice_enabled", True)

# Conversation history
history = [{"role": "system", "content": system_prompt}]

def chat_with_text(user_text, history_state):
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
        reply = f"Error: {e}\n\nMake sure Ollama is running and model '{model}' is pulled (ollama pull {model})"
    history_state.append({"role": "assistant", "content": reply})
    if voice_enabled:
        speak_text(reply)
    return reply, history_state

def update_chatbot(history_state):
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

# Build UI
with gr.Blocks(title="My Voice AI Companion", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 💬 My AI Companion – Voice & Text")
    gr.Markdown("Speak into your microphone or type. She will answer in text **and voice**.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🎤 Speak to her")
            mic_input = gr.Audio(source="microphone", type="filepath", label="Click microphone, speak, then 'Send Voice'")
            voice_btn = gr.Button("Send Voice", variant="primary")
            transcribed_text = gr.Textbox(label="What you said (transcribed)", interactive=False)
            voice_reply = gr.Textbox(label="Her voice reply (text)", lines=3, interactive=False)
        
        with gr.Column(scale=1):
            gr.Markdown("### ⌨️ Type to her")
            text_input = gr.Textbox(label="Your message", lines=2, placeholder="Type your message here...")
            text_btn = gr.Button("Send Text", variant="secondary")
            text_reply = gr.Textbox(label="Her text reply", lines=3, interactive=False)
    
    conversation = gr.Chatbot(label="Full Conversation", height=400)
    state = gr.State(history.copy())
    
    def text_flow(user_msg, hist_state):
        reply, new_hist = chat_with_text(user_msg, hist_state)
        chatbot_messages = update_chatbot(new_hist)
        return reply, new_hist, chatbot_messages, ""
    
    text_btn.click(
        fn=text_flow,
        inputs=[text_input, state],
        outputs=[text_reply, state, conversation, text_input]
    )
    
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
    
    demo.load(lambda s: update_chatbot(s), inputs=state, outputs=conversation)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
