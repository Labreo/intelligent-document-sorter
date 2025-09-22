import typer
from rich.console import Console
from core.agent import ComposioAgent

app = typer.Typer()
console = Console()

@app.command()
def start():
    """
    Starts the Composio Agent in an interactive chat session.
    """
    console.print("[bold magenta]====================== Composio Agent ======================[/bold magenta]\n")
    
    try:
        agent = ComposioAgent()
        agent.run_interactive_chat()  # <-- Call the new interactive method
    except Exception as e:
        console.print(f"[bold red]A critical error occurred: {e}[/bold red]")

if __name__ == "__main__":
    app()