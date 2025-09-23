import time
from rich.console import Console
from .constants import (
    COMPOSIO_CLIENT,
    GMAIL_TRIGGER_ID,
    COMPOSIO_USER_ID,
    GMAIL_AUTH_CONFIG_ID,
    GOOGLE_DRIVE_AUTH_CONFIG_ID
)
from .auth_config import ensure_connection 

console = Console()

class DocumentSorterAgent:
    def __init__(self):
        self.composio = COMPOSIO_CLIENT
        self.trigger_id = GMAIL_TRIGGER_ID
        self.user_id = COMPOSIO_USER_ID
        self.folder_ids = {} # To store Google Drive folder IDs
        
        console.print("\n[bold]================ Document Sorter Agent ================[/bold]")
        
        # 1. Ensure connections are active
        ensure_connection(self.composio, self.user_id, GMAIL_AUTH_CONFIG_ID, "Gmail")
        ensure_connection(self.composio, self.user_id, GOOGLE_DRIVE_AUTH_CONFIG_ID, "Google Drive")
        
        # 2. Check for and create necessary folders in Google Drive
        self._setup_drive_folders(['Invoices', 'Receipts', 'Purchase Orders', 'Uncategorized'])

        console.print("\n[bold green]✅ All connections verified and folders configured. Agent is ready.[/bold green]")

    def _setup_drive_folders(self, folder_names: list):
        """Checks if folders exist in Google Drive and creates them if not."""
        console.print("\n[bold]Configuring Google Drive folders...[/bold]")
        for name in folder_names:
            try:
                find_response = self.composio.tools.execute(
                    slug="GOOGLEDRIVE_FIND_FOLDER",
                    user_id=self.user_id,
                    arguments={"name_exact": name}
                )
                
                if not find_response.get("data", {}).get("files"):
                    console.print(f"   - Folder '[yellow]{name}[/yellow]' not found. Creating it...")
                    create_response = self.composio.tools.execute(
                        slug="GOOGLEDRIVE_CREATE_FOLDER",
                        user_id=self.user_id,
                        arguments={"folder_name": name}
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
        """Categorizes the document based on its filename."""
        lower_filename = filename.lower()
        if 'invoice' in lower_filename or 'inv_' in lower_filename:
            return 'Invoices'
        elif 'receipt' in lower_filename:
            return 'Receipts'
        elif 'purchase order' in lower_filename or 'po_' in lower_filename:
            return 'Purchase Orders'
        else:
            return 'Uncategorized'

    def start_listening(self):
        console.print(f"👂 Agent is now listening for trigger '[bold yellow]{self.trigger_id}[/bold yellow]'...")
        console.print("Press [bold red]Ctrl+C[/bold red] to stop the agent.")

        # --- FIX: Assign subscription to self to keep it in scope ---
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

            # Process all attachments, not just the first one
            for attachment in attachment_list:
                filename = attachment.get("filename", "unknown_file")
                attachment_id = attachment.get("attachmentId")
                
                if not attachment_id:
                    console.print(f"   - [yellow]Skipping attachment with no ID: {filename}[/yellow]")
                    continue

                console.print(f"\n   - [green]Processing attachment:[/green] {filename}")

                # Step 1: Download attachment
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

                # Step 2: Categorize the document
                category = self._categorize_document(filename)
                console.print(f"   - [cyan]   ↳ 🤖 Document categorized as:[/cyan] {category}")

                # Step 3: Upload to the correct Google Drive folder
                destination_folder_id = self.folder_ids.get(category)
                if not destination_folder_id:
                    console.print(f"   - [red]❌ Could not find a destination folder for '{category}'. Skipping upload.[/red]")
                    continue

                console.print(f"   - [blue]Uploading to Google Drive folder '{category}'...[/blue]")
                upload_result = self.composio.tools.execute(
                    slug="GOOGLEDRIVE_UPLOAD_FILE",
                    user_id=self.user_id,
                    arguments={
                        "file_to_upload": local_file_path,
                        "folder_to_upload_to": destination_folder_id
                    }
                )

                if upload_result.get("successful"):
                    file_name = upload_result.get("data", {}).get("name")
                    console.print(f"   - [bold green]   ↳ ✅ Successfully uploaded '{file_name}' to Google Drive![/bold green]")
                else:
                    console.print(f"   - [red]❌ Upload failed:[/red] {upload_result.get('error')}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold red]Shutdown signal received. Stopping agent...[/bold red]")