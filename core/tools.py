from .constants import COMPOSIO_CLIENT

def get_search_tools(user_id: str):
    """Fetches the specified search tools from Composio."""
    # You can add more tool names to this list as needed
    tool_names = ["COMPOSIO_SEARCH_DUCK_DUCK_GO_SEARCH"]
    
    print(f"Fetching tools for user '{user_id}': {tool_names}")
    return COMPOSIO_CLIENT.tools.get(user_id, tools=tool_names)