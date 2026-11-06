import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "IdeaFlow AI"
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Official Switch Infrastructure Configuration (Switch Console / switch-core v0.31.0)
    # Agent Protocol specification:
    # 1. Registration via POST /agents (with AGENT_REGISTRATION_TOKEN) -> yields live agent id & api_key
    # 2. SSE Inbound Stream via GET /agents/{id}/events?connection_id={uuid}&scope=all&filter=all&rooms={room_id}
    # 3. Connection Heartbeat via POST /agents/{id}/connection/beat (every 2-3s with generation fencing)
    # 4. Outbound Room Messaging via POST /agents/{id}/message
    # 5. Room Discovery & Moderation via GET/POST /agents/{id}/moderation/rooms
    SWITCH_URL: str = os.getenv("SWITCH_URL", "http://127.0.0.1:64008")
    AGENT_REGISTRATION_TOKEN: str = os.getenv("AGENT_REGISTRATION_TOKEN", "kTz6Ptm5vmGUEL0qt6o-IZfTS6eBEZ-A")
    AGENT_NAME: str = os.getenv("AGENT_NAME", "ideaflow-agent")
    AGENT_DISPLAY_NAME: str = "IdeaFlow Agent"
    AGENT_ID: Optional[str] = os.getenv("AGENT_ID", None)
    AGENT_SECRET: Optional[str] = os.getenv("AGENT_SECRET", None)
    SWITCH_ROOM_ID: str = os.getenv("SWITCH_ROOM_ID", "c8b5034b-3c6d-4b5c-9310-1cce324fa01a")
    CONNECTION_MODEL: str = "always_on"  # always_on | session_addressable
    
    # Discord Integration
    DISCORD_BOT_TOKEN: Optional[str] = os.getenv("DISCORD_BOT_TOKEN", None)
    DISCORD_GUILD_ID: Optional[str] = os.getenv("DISCORD_GUILD_ID", None)
    DISCORD_CHANNEL_ID: Optional[str] = os.getenv("DISCORD_CHANNEL_ID", None)
    
    # AI Engine Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "auto")  # auto | gemini | openai | creative_engine
    
    # Operational Mode
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")
    BUILTIN_SWITCH_ENABLED: bool = True

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
