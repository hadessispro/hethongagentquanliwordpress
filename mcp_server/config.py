import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    BASE_DIR: Path = BASE_DIR
    WORKSPACE_DIR: Path = Path(os.getenv("WORKSPACE_DIR", str(BASE_DIR))).resolve()
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Ngrok configuration
    NGROK_AUTHTOKEN: str = os.getenv("NGROK_AUTHTOKEN", "").strip()
    NGROK_DOMAIN: str = os.getenv("NGROK_DOMAIN", "").strip()
    
    # Security
    API_KEY: str = os.getenv("API_KEY", "").strip()
    ENABLE_COMMAND_EXECUTION: bool = os.getenv("ENABLE_COMMAND_EXECUTION", "true").lower() in ("1", "true", "yes")
    COMMAND_TIMEOUT_SECONDS: int = int(os.getenv("COMMAND_TIMEOUT_SECONDS", "60"))
    
    # Ponytail
    PONYTAIL_MODE: str = os.getenv("PONYTAIL_MODE", "full").lower()
    PONYTAIL_DIR: Path = BASE_DIR / "ponytail"

settings = Settings()
