# core/constants.py
import os
from dotenv import load_dotenv

from composio import Composio

# Load environment variables
load_dotenv()

# --- Initialize Composio Client ---
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
if not COMPOSIO_API_KEY:
    raise ValueError("COMPOSIO_API_KEY is not set in the .env file.")
COMPOSIO_CLIENT = Composio(api_key=COMPOSIO_API_KEY)


# --- User Configuration ---
COMPOSIO_USER_ID = os.getenv("COMPOSIO_USER_ID")
if not COMPOSIO_USER_ID:
    raise ValueError("COMPOSIO_USER_ID is not set in the .env file.")

# --- Document Sorter Config ---
GMAIL_TRIGGER_ID = os.getenv("GMAIL_TRIGGER_ID")
if not GMAIL_TRIGGER_ID:
    raise ValueError("GMAIL_TRIGGER_ID is not set in the .env file.")

PROCESS_LABEL_ID = os.getenv("PROCESS_LABEL_ID")
if not PROCESS_LABEL_ID:
    raise ValueError("PROCESS_LABEL_ID is not set in the .env file.")

GMAIL_AUTH_CONFIG_ID = os.getenv("GMAIL_AUTH_CONFIG_ID")
if not GMAIL_AUTH_CONFIG_ID:
    raise ValueError("GMAIL_AUTH_CONFIG_ID is not set.")

GOOGLE_DRIVE_AUTH_CONFIG_ID = os.getenv("GOOGLE_DRIVE_AUTH_CONFIG_ID")
if not GOOGLE_DRIVE_AUTH_CONFIG_ID:
    raise ValueError("GOOGLE_DRIVE_AUTH_CONFIG_ID is not set.")

print("✅ Clients and configurations loaded.")