from composio import Composio
from rich.console import Console

console = Console()

def ensure_connection(composio: Composio, user_id: str, auth_config_id: str):
    """
    Checks for an existing connection or initiates a new one and waits for it.
    
    Args:
        composio: The Composio client instance.
        user_id: The external user ID.
        auth_config_id: The specific auth config ID for the service (e.g., Gmail).
        
    Returns:
        The established connected_account object.
    """
    console.print(f"Checking connection for auth config: [bold yellow]{auth_config_id}[/bold yellow]...")
    
    # In a real app, you would first check if a connection already exists for this user.
    # For now, we will initiate a new one every time for simplicity.
    
    connection_request = composio.connected_accounts.initiate(
        user_id=user_id,
        auth_config_id=auth_config_id,
    )

    # Redirect user to the OAuth flow
    redirect_url = connection_request.redirect_url
    console.print(f"\n[bold magenta]Please authorize the app by visiting this URL:[/bold magenta]")
    console.print(f"[link={redirect_url}]{redirect_url}[/link]\n")

    # Wait for the connection to be established
    console.print("Waiting for you to complete the authorization in your browser...")
    connected_account = connection_request.wait_for_connection()
    
    console.print("[bold green]✔ Connection established successfully![/bold green]")
    return connected_account