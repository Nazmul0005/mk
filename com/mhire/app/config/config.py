import os
from dotenv import load_dotenv
            
load_dotenv()

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.openai_api_key = os.getenv("OPENAI_API_KEY")
            cls._instance.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
            cls._instance.openai_endpoint = os.getenv("OPENAI_ENDPOINT")
        return cls._instance