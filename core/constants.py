# agent_name/core/constants.py

import os
from dotenv import load_dotenv
from composio import Composio

# Load environment variables from .env file
load_dotenv()

# --- Initialize Composio Client ---
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
if not COMPOSIO_API_KEY:
    raise ValueError("COMPOSIO_API_KEY is not set in the .env file.")
COMPOSIO_CLIENT = Composio(api_key=COMPOSIO_API_KEY)

# --- User Configuration ---
# A unique identifier for the end-user running the agent
COMPOSIO_USER_ID = os.getenv("COMPOSIO_USER_ID", "default-user")

# --- Auth Config IDs ---
# These IDs tell Composio which application credentials to use for the OAuth flow.
GMAIL_AUTH_CONFIG_ID = os.getenv("GMAIL_AUTH_CONFIG_ID")
if not GMAIL_AUTH_CONFIG_ID:
    raise ValueError("GMAIL_AUTH_CONFIG_ID is not set in the .env file.")

GOOGLE_DRIVE_AUTH_CONFIG_ID = os.getenv("GOOGLE_DRIVE_AUTH_CONFIG_ID")
if not GOOGLE_DRIVE_AUTH_CONFIG_ID:
    raise ValueError("GOOGLE_DRIVE_AUTH_CONFIG_ID is not set in the .env file.")