# modules/llm_functions.py

from dotenv import load_dotenv, find_dotenv, set_key
import os

def load_api_keys():
    """Load API keys from the .env file and return them."""
    found_dotenv = find_dotenv('/Users/sahillakhe/repositories/secrets/keys.env', usecwd=True)
    load_dotenv(found_dotenv)
    
    openai_api_key = os.getenv("api_key_openai")
    google_api_key = os.getenv("api_key_google")
    cohere_api_key = os.getenv("api_key_cohere")

    return openai_api_key, google_api_key, cohere_api_key

def save_api_key(service, key):
    """Save a specific API key to the .env file."""
    env_path = find_dotenv('/Users/sahillakhe/repositories/secrets/keys.env', usecwd=True)
    set_key(env_path, service, key)