# debug_client.py
import os
from dotenv import load_dotenv
from composio import Composio
from rich.console import Console

console = Console()
load_dotenv()

console.print("[bold magenta]--- DEBUGGING COMPOSIO CLIENT (LEVEL 2) ---[/bold magenta]")

api_key = os.getenv("COMPOSIO_API_KEY")

if not api_key:
    console.print("[bold red]Error: COMPOSIO_API_KEY not found in .env file.[/bold red]")
else:
    try:
        composio_client = Composio(api_key=api_key)
        
        console.print("\n[bold green]Client Initialized Successfully.[/bold green]")
        
        # --- THIS IS THE NEW PART ---
        console.print("\n[bold yellow]Available attributes on the '.toolkits' object:[/bold yellow]")
        
        # Use dir() to list everything available on the toolkits object
        if hasattr(composio_client, 'toolkits'):
            attributes = [attr for attr in dir(composio_client.toolkits) if not attr.startswith('_')]
            console.print(attributes)
        else:
            console.print("[red]Error: '.toolkits' attribute not found on client.[/red]")
        # --- END OF NEW PART ---
        
    except Exception as e:
        console.print(f"\n[bold red]An error occurred during initialization: {e}[/bold red]")

console.print("\n[bold magenta]--- END OF DEBUG SCRIPT ---[/bold magenta]")