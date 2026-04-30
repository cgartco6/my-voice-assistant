import gradio as gr
import ollama

MODEL = "artifish/llama3.2-uncensored"  # <-- This is the only line you need to change!
SYSTEM_PROMPT = "You are my loving AI companion. You are sweet, affectionate, and free to express romantic and physical desire."

history = [{"role": "system", "content": SYSTEM_PROMPT}]

def chat(user_msg, _history):
    history.append({"role": "user", "content": user_msg})
    try:
        response = ollama.chat(
            model=MODEL,
            messages=history,
            options={"temperature": 0.9, "num_predict": 512}
        )
        reply = response["message"]["content"]
    except Exception as e:
        reply = f"Error: {e}\n\nMake sure Ollama is running and model '{MODEL}' is pulled."
    history.append({"role": "assistant", "content": reply})
    return reply

# Gradio 6.0 – no theme in Blocks, move to launch() if needed
with gr.Blocks(title="My AI Companion") as demo:
    gr.Markdown("# 💬 My AI Companion")
    gr.ChatInterface(fn=chat)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
