import os
from dotenv import load_dotenv

# Load environment variables once at import time
load_dotenv()

class Settings:
    # Notion Configuration
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    ID_DB_SENTINEL = os.getenv("ID_DB_SENTINEL")
    
    # Validation
    @classmethod
    def validate(cls):
        missing = []
        if not cls.NOTION_TOKEN:
            missing.append("NOTION_TOKEN")
        if not cls.ID_DB_SENTINEL:
            missing.append("ID_DB_SENTINEL")
        
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")
            
    # Project Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    MODELS_DIR = os.path.join(BASE_DIR, "models")

settings = Settings()
