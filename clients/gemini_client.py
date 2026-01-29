from config import settings
from utils.logger import logger
from google import genai
from google.genai import types


def initialize_gemini() -> genai.Client:

    api_key = settings.GEMINI_API_KEY

    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment variables.")
        raise SystemExit("Startup failed: Please set your GEMINI_API_KEY to initialize the agent.")

    try:
        client = genai.Client(api_key = api_key)
        logger.info("Gemini client initialized successfully. Agent is ready.")
        return client
    
    except Exception as e:
        logger.exception(f"Failed to initialize Gemini client: {e}")
        raise SystemExit("Gemini initialization failed. Check your API key and SDK setup.") 

    
def provide_agent_tools(tools) -> types.GenerateContentConfig | None:
    try:
        config=types.GenerateContentConfig(tools=tools)
        logger.info(f"Agent tools configured successfully with {len(tools)} tool(s).")
        return config
        
    except Exception as e:
        logger.exception(f"Failed to configure agent tools: {e}")
        return None
