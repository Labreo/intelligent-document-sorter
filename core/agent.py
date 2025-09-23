import time
from rich.console import Console
from .constants import (
    COMPOSIO_CLIENT,
    GMAIL_TRIGGER_ID,
    COMPOSIO_USER_ID,
    GMAIL_AUTH_CONFIG_ID,
)
# Corrected import path as you noted
from .auth_config import ensure_connection 

console = Console()

class DocumentSorterAgent:
    def __init__(self):
        self.composio = COMPOSIO_CLIENT
        self.trigger_id = GMAIL_TRIGGER_ID
        self.user_id = COMPOSIO_USER_ID
        
        console.print("\n[bold]================ Document Sorter Agent ================[/bold]")
        ensure_connection(self.composio, self.user_id, GMAIL_AUTH_CONFIG_ID, "Gmail")
        console.print("\n[bold green]✅ All connections verified. Agent is ready.[/bold green]")

    def start_listening(self):
        console.print(f"👂 Agent is now listening for trigger '[bold yellow]{self.trigger_id}[/bold yellow]'...")
        console.print("Press [bold red]Ctrl+C[/bold red] to stop the agent.")

        subscription = self.composio.triggers.subscribe()

        @subscription.handle(trigger_id=self.trigger_id)
        def handle_new_email(data):
            console.print("\n🚀 New email detected! Executing workflow...")

            email_payload = data.get("payload", {})
            message_id = email_payload.get("message_id")
            attachment_list = email_payload.get("attachment_list", [])

            if not message_id or not attachment_list:
                console.print("   - [yellow]Email has no attachments or is missing a message_id. Skipping.[/yellow]")
                return

            attachment = attachment_list[0]
            attachment_id = attachment.get("attachmentId")
            filename = attachment.get("filename", "unknown_file")
            
            console.print(f"   - [green]Attachment found:[/green] {filename}")

            console.print("   - [blue]Downloading from Gmail...[/blue]")
            download_result = self.composio.tools.execute(
                slug="GMAIL_GET_ATTACHMENT",
                user_id=self.user_id,
                arguments={"message_id": message_id, "attachment_id": attachment_id, "file_name": filename}
            )

            if not download_result.get("successful"):
                console.print(f"   - [red]❌ Download failed:[/red] {download_result.get('error')}")
                return
            
            # --- THE FIX ---
            # Get the local file path from the correct key in the result
            local_file_path = download_result["data"]["file"]
            
            console.print(f"   - [bold green]   ↳ ✅ Download successful! Saved to:[/bold green] {local_file_path}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold red]Shutdown signal received. Stopping agent...[/bold red]")