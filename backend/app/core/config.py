import os
from pathlib import Path
from typing import Optional

class Settings:
    # Application settings
    APP_NAME: str = "QCYIS Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Ollama settings
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    
    # MediaPipe settings
    MEDIAPIPE_MODEL_COMPLEXITY: int = int(os.getenv("MEDIAPIPE_MODEL_COMPLEXITY", "2"))
    MEDIAPIPE_MIN_DETECTION_CONFIDENCE: float = float(os.getenv("MEDIAPIPE_MIN_DETECTION_CONFIDENCE", "0.7"))
    MEDIAPIPE_MIN_TRACKING_CONFIDENCE: float = float(os.getenv("MEDIAPIPE_MIN_TRACKING_CONFIDENCE", "0.5"))
    
    # Consciousness analysis settings
    CONSCIOUSNESS_SAMPLING_RATE: int = int(os.getenv("CONSCIOUSNESS_SAMPLING_RATE", "256"))
    CONSCIOUSNESS_WINDOW_SIZE: int = int(os.getenv("CONSCIOUSNESS_WINDOW_SIZE", "1024"))
    
    # Data storage settings
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "./data"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Performance settings
    MAX_CONCURRENT_CONNECTIONS: int = int(os.getenv("MAX_CONCURRENT_CONNECTIONS", "100"))
    WEBSOCKET_TIMEOUT: int = int(os.getenv("WEBSOCKET_TIMEOUT", "300"))

settings = Settings()
