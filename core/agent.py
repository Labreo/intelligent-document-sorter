import time
import os
import json # <-- Add this import
from datetime import date # <-- Add this import
from rich.console import Console
from docstrange import DocumentExtractor

from .constants import (
    COMPOSIO_CLIENT,
    COMPOSIO_USER_ID,
    GMAIL_AUTH_CONFIG_ID,
    GOOGLE_DRIVE_AUTH_CONFIG_ID
)
from .auth_config import ensure_connection 

console = Console()

class DocumentSorterAgent:
    def __init__(self):
        # ... __init__ is largely the same, just removed the old category method
        self.composio = COMPOSIO_CLIENT
        self.user_id = COMPOSIO_USER_ID
        self.folder_ids = {} 
        
        console.print("\n[bold]================ Document Sorter Agent Initialising ================[/bold]")
        
        try:
            self.extractor = DocumentExtractor()
            console.print("[green]✓ DocStrange Extractor Initialized.[/green]")
        except Exception as e:
            console.print(f"[bold red]❌ Failed to initialize DocStrange. Please run 'docstrange login'. Error: {e}[/bold red]")
            return

        gmail_connection = ensure_connection(self.composio, self.user_id, GMAIL_AUTH_CONFIG_ID, "Gmail")
        self.trigger_id = self._get_or_create_trigger(gmail_connection.id)
        if not self.trigger_id:
            console.print("[bold red]❌ Critical error: Failed to set up trigger. Agent cannot start.[/bold red]")
            return

        ensure_connection(self.composio, self.user_id, GOOGLE_DRIVE_AUTH_CONFIG_ID, "Google Drive")
        self._setup_drive_folders(['Invoices', 'Receipts', 'Purchase Orders', 'Uncategorized'])

        console.print("\n[bold green]✅ All connections verified and folders configured. Agent is ready.[/bold green]")

    def _get_or_create_trigger(self, connected_account_id: str) -> str | None:
        # This method remains unchanged
        console.print("\n[bold]Configuring Gmail Trigger...[/bold]")
        try:
            triggers = self.composio.triggers.list_active(
                trigger_names=["GMAIL_NEW_GMAIL_MESSAGE"], connected_account_ids=[connected_account_id],
            )
            if triggers.items:
                trigger_id = triggers.items[0].id
                console.print(f"   - [green]✓ Found existing active trigger:[/green] {trigger_id}")
                return trigger_id
            
            console.print("   - No active trigger found. Creating a new one...")
            response = self.composio.triggers.create(
                slug="GMAIL_NEW_GMAIL_MESSAGE", connected_account_id=connected_account_id, trigger_config={},
            )
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
    
    # --- V2.1: REFACTORED HELPER METHODS ---
    def _extract_text_with_docstrange(self, file_path: str) -> str | None:
        """Uses DocStrange to extract text content from a file."""
        console.print("   - [blue]   ↳ 🧠 Extracting text with DocStrange...[/blue]")
        try:
            result = self.extractor.extract(file_path)
            return result.extract_markdown()
        except Exception as e:
            console.print(f"   - [red]❌ DocStrange extraction failed: {e}[/red]")
            return None

    def _extract_structured_data_with_gemini(self, document_text: str) -> dict | None:
        """Uses Gemini to classify the document and extract structured data."""
        console.print("   - [blue]   ↳ 🤖 Asking Gemini to classify and extract data...[/blue]")

        # A more universal prompt that asks for classification AND data extraction
        prompt = f"""
        Analyze the document text and perform two tasks:
        1. Classify the document_type as one of: 'Invoice', 'Receipt', 'Purchase Order', or 'Other'.
        2. Extract the following fields. If a field is not present or not applicable, use "N/A".
            - document_type: The type of document.
            - vendor_name: The name of the company or vendor on the document.
            - document_id: The invoice number, receipt ID, or PO number.
            - document_date: The primary date on the document (invoice date, receipt date, etc.), in YYYY-MM-DD format.
            - total_amount: The final total amount, as a number.

        Provide the output as a single, clean JSON object with no additional text or formatting.

        --- DOCUMENT TEXT ---
        {document_text[:8000]} 
        --- END OF TEXT ---
        """
        try:
            response = self.composio.tools.execute(
                slug="GEMINI_GENERATE_CONTENT",
                user_id=self.user_id,
                arguments={
                    "model": "gemini-1.5-flash",
                    "prompt": prompt,
                    "temperature": 0.0,
                    # For Gemini, you can suggest JSON output in the prompt
                    # and often it's smart enough. Some models have a specific JSON mode.
                }
            )
            
            # Extract the raw text from Gemini's response
            llm_response_str = response.get("data", {}).get("text", "")
            
            # Clean up potential markdown formatting around the JSON
            if llm_response_str.startswith("```json"):
                llm_response_str = llm_response_str[7:-4]

            if not llm_response_str:
                return None

            return json.loads(llm_response_str)

        except Exception as e:
            console.print(f"[red]   - ❌ Gemini data extraction failed: {e}[/red]")
            return None

    def _rename_file_from_data(self, structured_data: dict, original_path: str) -> str:
        """Creates a standardized filename from extracted data and renames the local file."""
        try:
            doc_date = structured_data.get("document_date") or date.today().isoformat()
            vendor = structured_data.get("vendor_name", "UnknownVendor")
            doc_id = structured_data.get("document_id", "NoID")
            
            # Sanitize parts to make them filename-safe
            vendor = "".join(c for c in vendor if c.isalnum() or c in " -_").rstrip()
            doc_id = "".join(c for c in doc_id if c.isalnum() or c in " -_").rstrip()

            _, extension = os.path.splitext(original_path)
            directory = os.path.dirname(original_path)
            
            new_filename = f"{doc_date}_{vendor}_{doc_id}{extension}"
            new_path = os.path.join(directory, new_filename)
            
            os.rename(original_path, new_path)
            
            console.print(f"   - [cyan]   ↳ 📝 Renamed file to:[/cyan] {new_filename}")
            return new_path
        except Exception as e:
            console.print(f"   - [red]❌ Error renaming file: {e}[/red]")
            return original_path

    def start_listening(self):
        if not hasattr(self, 'trigger_id') or not self.trigger_id:
            return

        console.print(f"👂 Agent is now listening for trigger '[bold yellow]{self.trigger_id}[/bold yellow]'...")
        console.print("Press [bold red]Ctrl+C[/bold red] to stop the agent.")
        self.subscription = self.composio.triggers.subscribe()

        @self.subscription.handle(trigger_id=self.trigger_id)
        def handle_new_email(data):
            # ... (email processing and attachment loop start is the same)
            email_payload, message_id, attachment_list = data.get("payload", {}), data.get("payload", {}).get("message_id"), data.get("payload", {}).get("attachment_list", [])

            if not message_id or not attachment_list: return

            for attachment in attachment_list:
                filename, attachment_id = attachment.get("filename", "unknown_file"), attachment.get("attachmentId")
                if not attachment_id: continue

                console.print(f"\n   - [green]Processing attachment:[/green] {filename}")
                download_result = self.composio.tools.execute(
                    slug="GMAIL_GET_ATTACHMENT", user_id=self.user_id,
                    arguments={"message_id": message_id, "attachment_id": attachment_id, "file_name": filename}
                )

                if not download_result.get("successful"):
                    console.print(f"   - [red]❌ Download failed.[/red]"); continue
                
                local_file_path = download_result["data"]["file"]
                console.print(f"   - [bold green]   ↳ ✅ Download successful![/bold green]")
                
                document_text = self._extract_text_with_docstrange(local_file_path)
                final_file_path = local_file_path
                category = "Uncategorized"

                if document_text:
                    structured_data = self._extract_structured_data_with_gemini(document_text)
                    if structured_data:
                        # Get category from AI's classification
                        doc_type_map = {
                            "Invoice": "Invoices", "Receipt": "Receipts", "Purchase Order": "Purchase Orders"
                        }
                        category = doc_type_map.get(structured_data.get("document_type"), "Uncategorized")
                        
                        # Rename the file using the extracted data
                        final_file_path = self._rename_file_from_data(structured_data, local_file_path)

                console.print(f"   - [cyan]   ↳ 🤖 Document categorized as:[/cyan] {category}")
                
                destination_folder_id = self.folder_ids.get(category)
                if not destination_folder_id:
                    console.print(f"   - [red]❌ Could not find a destination folder for '{category}'.[/red]"); continue

                console.print(f"   - [blue]Uploading to Google Drive folder '{category}'...[/blue]")
                upload_result = self.composio.tools.execute(
                    slug="GOOGLEDRIVE_UPLOAD_FILE", user_id=self.user_id,
                    arguments={"file_to_upload": final_file_path, "folder_to_upload_to": destination_folder_id}
                )

                if upload_result.get("successful"):
                    file_name = upload_result.get("data", {}).get("name")
                    console.print(f"   - [bold green]   ↳ ✅ Successfully uploaded '{file_name}' to Google Drive![/bold green]")
                else:
                    console.print(f"   - [red]❌ Upload failed.[/red]")

        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold red]Shutdown signal received. Stopping agent...[/bold red]")