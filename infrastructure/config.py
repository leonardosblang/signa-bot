import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.debug_mode = os.getenv("DEBUG_MODE", "False").lower() == "true"
        self.crawl_timeout = int(os.getenv("CRAWL_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.cache_enabled = os.getenv("CACHE_ENABLED", "True").lower() == "true"
        self.cache_ttl = int(os.getenv("CACHE_TTL", "3600"))
        
    def validate(self) -> bool:
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        return True
        
    def log_debug(self, message: str) -> None:
        if self.debug_mode:
            print(f"[DEBUG] {message}")

config = Config()