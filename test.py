from composio import Composio
from composio_google import GoogleProvider
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import json

load_dotenv()
# Create composio client
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
composio = Composio(api_key=COMPOSIO_API_KEY,provider=GoogleProvider())
# Create google client
client = genai.Client()

# User ID must be a valid UUID format
user_id = os.getenv("COMPOSIO_USER_ID") # Replace with actual user UUID from your database

# Get tools for Gmail

def clean_schema(obj):
    if isinstance(obj, dict):
        # Remove "examples" key if present
        obj.pop("examples", None)
        for k, v in list(obj.items()):
            clean_schema(v)
    elif isinstance(obj, list):
        for item in obj:
            clean_schema(item)
    return obj

# Get Gmail tools
tools = composio.tools.get(user_id=user_id, toolkits=["GMAIL"])

# Clean them to remove invalid fields
tools = [clean_schema(tool) for tool in tools]

# Debug: check if any "examples" survived
print(json.dumps(tools[0], indent=2)[:500])
# Create genai client config
config = types.GenerateContentConfig(tools=tools)

# Use the chat interface
chat = client.chats.create(model="gemini-2.0-flash", config=config)
response = chat.send_message("What can you do with Gmail?")
print("[!] Response:", response.text)
