from rich.console import Console
from google.genai import types
from .constants import GEMINI_CLIENT, COMPOSIO_USER_ID
from .tools import get_search_tools

console = Console()

class ComposioAgent:
    def __init__(self):
        console.print("[bold green]Initializing Composio Agent...[/bold green]")
        self.client = GEMINI_CLIENT
        
        tools = get_search_tools(user_id=COMPOSIO_USER_ID)
        config = types.GenerateContentConfig(tools=tools)
        self.chat = self.client.chats.create(model="gemini-2.0-flash", config=config)
        console.print("[bold green]Agent is ready. Chat session created.[/bold green]")

    def ask(self, prompt: str):
        """Sends a single prompt to the chat and returns the response."""
        console.print(f"\n[bold blue]Sending prompt...[/]")
        response = self.chat.send_message(prompt)
        console.print("[bold green]Received response:[/bold green]")
        return response.text
        
    def run_interactive_chat(self):
        """Starts a continuous chat loop until the user types 'exit' or 'quit'."""
        console.print("\n[bold]Starting interactive chat. Type 'quit' or 'exit' to end the session.[/bold]")
        while True:
            prompt = console.input("[bold cyan]You: [/bold cyan]")
            if prompt.lower() in ["quit", "exit"]:
                console.print("[bold red]Ending chat session.[/bold red]")
                break
            
            response_text = self.ask(prompt)
            console.print(f"[bold yellow]Agent:[/bold yellow] {response_text}")