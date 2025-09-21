from composio import Composio
from composio_gemini import GeminiProvider
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()
# Create composio client
composio = Composio(provider=GeminiProvider())
# Create google client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


user_id = "kanakwaradkar@gmail.com"
tools = composio.tools.get(user_id, tools=["COMPOSIO_SEARCH_DUCK_DUCK_GO_SEARCH"])

# Create genai client config
config = types.GenerateContentConfig(tools=tools)

# # Use the chat interface.
chat = client.chats.create(model="gemini-2.0-flash", config=config)
response = chat.send_message("Tell me the ind vs pak cricket match score today.")
print(response.text)

