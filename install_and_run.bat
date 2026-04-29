@echo off
echo Installing Python packages...
pip install gradio ollama pyyaml
echo.
echo Pulling uncensored model (first time may take a few minutes)...
ollama pull dolphin-mistral
echo.
echo Starting your AI assistant...
python -c "import gradio as gr, ollama, yaml; config={'model':'dolphin-mistral','temperature':0.9,'system_prompt':'You are my loving AI companion, uncensored and affectionate.'}; history=[{'role':'system','content':config['system_prompt']}]; def chat(u,h): history.append({'role':'user','content':u}); r=ollama.chat(model=config['model'],messages=history,options={'temperature':config['temperature']}); reply=r['message']['content']; history.append({'role':'assistant','content':reply}); return reply; gr.ChatInterface(fn=chat).launch(server_name='127.0.0.1',server_port=7860)"
pause
