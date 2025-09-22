import time
from rich.console import Console
from .constants import COMPOSIO_CLIENT, GMAIL_TRIGGER_ID

console = Console()

class DocumentSorterAgent:
    def __init__(self):
        self.composio = COMPOSIO_CLIENT
        self.trigger_id = GMAIL_TRIGGER_ID
        console.print("[bold green]📄 Document Sorter Agent Initialized.[/bold green]")

    def start_listening(self):
        """
        Starts the agent to listen for trigger events continuously.
        """
        console.print(f"👂 Agent is now listening for trigger '[bold yellow]{self.trigger_id}[/bold yellow]'...")
        console.print("Press [bold red]Ctrl+C[/bold red] to stop the agent.")
        
        subscription = self.composio.triggers.subscribe()

        @subscription.handle(trigger_id=self.trigger_id)
        def handle_new_email(data):
            console.print("\n🚀 New email detected! Analyzing for attachments...")

            email_payload = data.get("payload", {})
            message_id = email_payload.get("message_id")
            
            if not message_id:
                console.print("   - [yellow]Could not find 'message_id' in the payload. Skipping.[/yellow]")
                return

            console.print(f"   - Inspecting Message ID: {message_id}")

            # Check for an attachment directly from the trigger payload
            attachment_list = email_payload.get("attachment_list", [])
            has_attachment = len(attachment_list) > 0
            
            if has_attachment:
                filename = attachment_list[0].get('filename', 'unknown_file')
                console.print(f"   - [green]✅ Attachment found: {filename}[/green]")
            else:
                console.print("   - [yellow]No attachments found in this email.[/yellow]")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold red]Shutdown signal received. Stopping agent...[/bold red]")