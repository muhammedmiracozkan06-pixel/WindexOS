#!/usr/bin/env python3
import os
from groq import Groq
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

KEY_FILE = "/Windex/System64/config/api.key"

def get_api_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return f.read().strip()
    return None

console = Console()
api_key = get_api_key()

if not api_key:
    console.print("[bold red]Hata: API anahtarı bulunamadı![/bold red]")
    exit()

client = Groq(api_key=api_key)

def chat():
    console.clear()
    console.print(Panel(f"PilotAI | Model: openai/gpt-oss-120b", style="bold yellow"))
    
    messages = [{"role": "system", "content": "Sen bir terminal asistanısın. Sudo veya root yetkisi gerektiren komutları asla çalıştırma."}]
    
    while True:
        try:
            user_input = console.input("[bold green]Siz > [/bold green]")
            if user_input.lower() in ["exit", "quit"]: break
            
            messages.append({"role": "user", "content": user_input})
            
            chat_completion = client.chat.completions.create(
                messages=messages,
                model="openai/gpt-oss-120b"
            )
            
            response = chat_completion.choices[0].message.content
            messages.append({"role": "assistant", "content": response})
            
            console.print(Panel(Markdown(response), title="PilotAI", border_style="green"))
            
        except Exception as e:
            console.print(f"[bold red]Hata:[/bold red] {e}")

if __name__ == "__main__":
    chat()
