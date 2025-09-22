# core/constants.py
import os
from dotenv import load_dotenv
from google import genai
from composio import Composio
from composio_gemini import GeminiProvider

# Load environment variables
load_dotenv()

# --- Initialize Google AI Client ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the .env file.")
GEMINI_CLIENT = genai.Client(api_key=GOOGLE_API_KEY)

# --- Initialize Composio Client ---
COMPOSIO_CLIENT = Composio(provider=GeminiProvider())

# --- User Configuration ---
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
if not COMPOSIO_API_KEY:
    raise ValueError("COMPOSIO_API_KEY is not set in the .env file.")

COMPOSIO_USER_ID = os.getenv("COMPOSIO_USER_ID")
if not COMPOSIO_USER_ID:
    raise ValueError("COMPOSIO_USER_ID is not set in the .env file.")

# --- Initialize Nanonets ---
NANONETS_API_KEY = os.getenv("NANONETS_API_KEY")
if not NANONETS_API_KEY:
    raise ValueError("NANONETS_API_KEY is not set in the .env file.")

print(" Clients and configurations loaded.")