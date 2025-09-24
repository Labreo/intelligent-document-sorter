import time
from rich.console import Console
from .constants import (
    COMPOSIO_CLIENT,
    # GMAIL_TRIGGER_ID, # No longer needed
    COMPOSIO_USER_ID,
    GMAIL_AUTH_CONFIG_ID,
    GOOGLE_DRIVE_AUTH_CONFIG_ID
)
from .auth_config import ensure_connection 

console = Console()

class DocumentSorterAgent:
    def __init__(self):
        self.composio = COMPOSIO_CLIENT
        self.user_id = COMPOSIO_USER_ID
        self.folder_ids = {} # To store Google Drive folder IDs
        
        console.print("\n[bold]================ Document Sorter Agent Initialising ================[/bold]")
        
        # --- UPDATED WORKFLOW ---
        # 1. First, establish the Gmail connection to get the necessary ID for the trigger.
        gmail_connection = ensure_connection(self.composio, self.user_id, GMAIL_AUTH_CONFIG_ID, "Gmail")

        # 2. Programmatically get or create the trigger for that specific account.
        self.trigger_id = self._get_or_create_trigger(gmail_connection.id)
        if not self.trigger_id:
            console.print("[bold red]❌ Critical error: Failed to set up trigger. Agent cannot start.[/bold red]")
            return # Stop initialization if trigger setup fails

        # 3. Now, set up the remaining connections and folders.
        ensure_connection(self.composio, self.user_id, GOOGLE_DRIVE_AUTH_CONFIG_ID, "Google Drive")
        self._setup_drive_folders(['Invoices', 'Receipts', 'Purchase Orders', 'Uncategorized'])

        console.print("\n[bold green]✅ All connections verified and folders configured. Agent is ready.[/bold green]")

    def _get_or_create_trigger(self, connected_account_id: str) -> str | None:
        """Checks for an active trigger or creates one if it doesn't exist."""
        console.print("\n[bold]Configuring Gmail Trigger...[/bold]")
        try:
            # Check if a trigger for this account already exists
            triggers = self.composio.triggers.list_active(
                trigger_names=["GMAIL_NEW_GMAIL_MESSAGE"],
                connected_account_ids=[connected_account_id],
            )

            if triggers.items:
                trigger_id = triggers.items[0].id
                console.print(f"   - [green]✓ Found existing active trigger:[/green] {trigger_id}")
                return trigger_id

            # If no trigger exists, create one
            console.print("   - No active trigger found. Creating a new one...")
            response = self.composio.triggers.create(
                slug="GMAIL_NEW_GMAIL_MESSAGE",
                connected_account_id=connected_account_id,
                trigger_config={}, # Empty config watches the entire inbox
            )
            
            # --- FIX: The create response uses .trigger_id, not .id ---
            trigger_id = response.trigger_id
            
            console.print(f"   - [green]✓ Successfully created new trigger:[/green] {trigger_id}")
            return trigger_id

        except Exception as e:
            console.print(f"[bold red]   - ❌ Error configuring trigger: {e}[/bold red]")
            return None

    def _setup_drive_folders(self, folder_names: list):
        # This method remains unchanged
        console.print("\n[bold]Configuring Google Drive folders...[/bold]")
        for name in folder_names:
            try:
                find_response = self.composio.tools.execute(
                    slug="GOOGLEDRIVE_FIND_FOLDER", user_id=self.user_id, arguments={"name_exact": name}
                )
                if not find_response.get("data", {}).get("files"):
                    console.print(f"   - Folder '[yellow]{name}[/yellow]' not found. Creating it...")
                    create_response = self.composio.tools.execute(
                        slug="GOOGLEDRIVE_CREATE_FOLDER", user_id=self.user_id, arguments={"folder_name": name}
                    )
                    folder_id = create_response.get("data", {}).get("id")
                    console.print(f"   - [green]✓ Created folder '{name}'[/green]")
                else:
                    folder_id = find_response["data"]["files"][0]["id"]
                    console.print(f"   - [green]✓ Found folder '{name}'[/green]")
                self.folder_ids[name] = folder_id
            except Exception as e:
                console.print(f"[bold red]Error setting up folder {name}: {e}[/bold red]")

    def _categorize_document(self, filename: str) -> str:
        # This method remains unchanged
        lower_filename = filename.lower()
        if 'invoice' in lower_filename or 'inv_' in lower_filename: return 'Invoices'
        elif 'receipt' in lower_filename: return 'Receipts'
        elif 'purchase order' in lower_filename or 'po_' in lower_filename: return 'Purchase Orders'
        else: return 'Uncategorized'

    def start_listening(self):
        if not hasattr(self, 'trigger_id') or not self.trigger_id:
            console.print("[bold red]Agent cannot listen: Trigger ID was not set during initialization.[/bold red]")
            return

        console.print(f"👂 Agent is now listening for trigger '[bold yellow]{self.trigger_id}[/bold yellow]'...")
        console.print("Press [bold red]Ctrl+C[/bold red] to stop the agent.")

        # Assign subscription to self to keep it in scope
        self.subscription = self.composio.triggers.subscribe()

        @self.subscription.handle(trigger_id=self.trigger_id)
        def handle_new_email(data):
            # This logic remains unchanged
            console.print("\n🚀 New email detected! Executing workflow...")
            email_payload = data.get("payload", {})
            message_id = email_payload.get("message_id")
            attachment_list = email_payload.get("attachment_list", [])

            if not message_id or not attachment_list:
                console.print("   - [yellow]Email has no attachments or is missing a message_id. Skipping.[/yellow]")
                return

            for attachment in attachment_list:
                filename = attachment.get("filename", "unknown_file")
                attachment_id = attachment.get("attachmentId")
                if not attachment_id:
                    console.print(f"   - [yellow]Skipping attachment with no ID: {filename}[/yellow]")
                    continue

                console.print(f"\n   - [green]Processing attachment:[/green] {filename}")
                console.print("   - [blue]Downloading from Gmail...[/blue]")
                download_result = self.composio.tools.execute(
                    slug="GMAIL_GET_ATTACHMENT",
                    user_id=self.user_id,
                    arguments={"message_id": message_id, "attachment_id": attachment_id, "file_name": filename}
                )

                if not download_result.get("successful"):
                    console.print(f"   - [red]❌ Download failed:[/red] {download_result.get('error')}")
                    continue
                
                local_file_path = download_result["data"]["file"]
                console.print(f"   - [bold green]   ↳ ✅ Download successful! Saved to:[/bold green] {local_file_path}")

                category = self._categorize_document(filename)
                console.print(f"   - [cyan]   ↳ 🤖 Document categorized as:[/cyan] {category}")

                destination_folder_id = self.folder_ids.get(category)
                if not destination_folder_id:
                    console.print(f"   - [red]❌ Could not find a destination folder for '{category}'. Skipping upload.[/red]")
                    continue

                console.print(f"   - [blue]Uploading to Google Drive folder '{category}'...[/blue]")
                upload_result = self.composio.tools.execute(
                    slug="GOOGLEDRIVE_UPLOAD_FILE",
                    user_id=self.user_id,
                    arguments={"file_to_upload": local_file_path, "folder_to_upload_to": destination_folder_id}
                )

                if upload_result.get("successful"):
                    file_name = upload_result.get("data", {}).get("name")
                    console.print(f"   - [bold green]   ↳ ✅ Successfully uploaded '{file_name}' to Google Drive![/bold green]")
                else:
                    console.print(f"   - [red]❌ Upload failed:[/red] {upload_result.get('error')}")

        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold red]Shutdown signal received. Stopping agent...[/bold red]")