# Intelligent Document Sorter

An automated agent that monitors a Gmail account for new attachments, intelligently classifies them using AI, and files them with standardized names into a designated Google Drive.

-----

## Core Features

  * **Automated Email Processing:** Programmatically creates and monitors a trigger for new messages in a Gmail inbox, automatically downloading any attachments for processing.
  * **Content-Based Document Classification:** Utilizes OCR via **DocStrange** to extract text from various document formats (including PDFs and images) and leverages **Google's Gemini** model for intelligent, content-based classification (e.g., Invoice, Receipt).
  * **AI-Powered Data Extraction and File Standardization:** Extracts key data points such as vendor name, document ID, date, and total amount. This data is then used to programmatically rename files to a consistent, standardized format (e.g., `YYYY-MM-DD_VendorName_DocID.pdf`).
  * **Automated Google Drive Filing:** Automatically creates categorized folders within Google Drive (`Invoices`, `Receipts`, etc.) and uploads the standardized files to the appropriate location.
  * **Temporary File Cleanup:** Automatically deletes local temporary files after they have been successfully processed and uploaded to Google Drive, ensuring the system remains clean.

-----

## Technology Stack

  * **Core:** Python 3.12+
  * **Framework/SDKs:** Composio, DocStrange
  * **AI Model:** Google Gemini (via Composio)
  * **Integrations:** Gmail, Google Drive
  * **CLI & Logging:** Typer, Rich
  * **Package Management:** uv

-----

## Setup and Installation

Follow these steps to configure and run the agent on a local machine.

#### 1\. Clone the Repository

```bash
git clone https://github.com/your-username/intelligent-document-sorter.git
cd intelligent-document-sorter
```

#### 2\. Create and Activate the Virtual Environment

This project uses `uv` for package management.

```bash
# Create the virtual environment
uv venv

# Activate the environment
source .venv/bin/activate
```

#### 3\. Install Dependencies

```bash
# Assuming a requirements.txt file exists
uv pip install -r requirements.txt
```

*(Note: If `requirements.txt` does not exist, it can be generated with `uv pip freeze > requirements.txt`)*

#### 4\. Configure Environment Variables

Create a `.env` file from the provided example and populate it with your credentials.

```bash
cp .env.example .env
```

Edit the `.env` file and provide values for the following variables:

  * `COMPOSIO_API_KEY`: Your API key from the Composio Dashboard.
  * `COMPOSIO_USER_ID`: A unique identifier for the user instance (e.g., `user-001`).
  * `GMAIL_AUTH_CONFIG_ID`: The Auth Config ID for Gmail from your Composio Dashboard.
  * `GOOGLE_DRIVE_AUTH_CONFIG_ID`: The Auth Config ID for Google Drive from your Composio Dashboard.

#### 5\. Authenticate DocStrange

This is a one-time command to authenticate the DocStrange CLI with your account.

```bash
docstrange login
```

Follow the on-screen prompts to complete the authentication process.

-----

## Usage

#### 1\. Activate the Environment

For each new terminal session, activate the virtual environment before running the application.

```bash
source .venv/bin/activate
```

#### 2\. Start the Agent

Execute the main script using the `start` command defined in the Typer CLI.

```bash
python main.py start
```

Upon execution, the agent initializes and performs its setup sequence, which includes verifying connections, configuring triggers, and ensuring Drive folders exist. The agent is fully operational once the message `👂 Agent is now listening for trigger...` is displayed in the console. It will now run continuously, monitoring the specified Gmail account for new attachments.

To terminate the agent, press **`Ctrl+C`** in the terminal.

