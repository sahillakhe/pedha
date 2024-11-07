# modules/llm_functions.py

import os
from dotenv import load_dotenv, find_dotenv, set_key

def load_api_keys(env_path=None):
    """Load API keys from the .env file and return them."""
    if env_path:
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            print(f"Warning: Specified .env file at {env_path} does not exist.")
    else:
        found_dotenv = find_dotenv()
        if found_dotenv:
            load_dotenv(found_dotenv)
        else:
            print("Warning: .env file not found. Please ensure that it exists.")
    
    openai_api_key = os.getenv("api_key_openai")
    return openai_api_key

def save_api_key(service, key, env_path=None):
    """Save a specific API key to the .env file."""
    if env_path:
        if not os.path.exists(env_path):
            # Create the file if it doesn't exist
            open(env_path, 'a').close()
        set_key(env_path, service, key)
    else:
        env_path = find_dotenv()
        if not env_path:
            # Create a new .env file in the current directory
            env_path = os.path.join(os.getcwd(), '.env')
            open(env_path, 'a').close()
        set_key(env_path, service, key)
