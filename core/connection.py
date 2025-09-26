# agent_name/core/connection.py

from composio import Composio
from rich.console import Console

console = Console()

def ensure_connection(composio: Composio, user_id: str, auth_config_id: str, app_name: str):
    """
    Checks for an active connection or initiates a new one.
    Returns the connected_account object.
    """
    console.print(f"Verifying connection for [bold cyan]{app_name}[/bold cyan]...")

    # 1. Check for an existing active connection
    try:
        connections = composio.connected_accounts.list(user_id=user_id)
        for conn in connections:
            if conn.auth_config_id == auth_config_id and conn.status == "active":
                console.print(f"[green]✔ Active {app_name} connection found.[/green]")
                return conn
    except Exception:
        pass # Proceed to initiate a new connection if listing fails

    # 2. If no active connection is found, initiate a new one
    console.print(f"[yellow]No active {app_name} connection found. Starting setup...[/yellow]")
    connection_request = composio.connected_accounts.initiate(
        user_id=user_id,
        auth_config_id=auth_config_id,
    )

    # 3. Redirect user and wait for completion
    redirect_url = connection_request.redirect_url
    console.print(f"\n[bold magenta]ACTION REQUIRED: Please authorize {app_name} by visiting this URL:[/bold magenta]")
    console.print(f"[link={redirect_url}]{redirect_url}[/link]\n")
    console.print("Waiting for you to complete the authorization in your browser...")
    
    connected_account = connection_request.wait_for_connection()
    
    console.print(f"[bold green]✔ {app_name} connection established successfully![/bold green]")
    
    return connected_account