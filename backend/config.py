import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "IdeaFlow AI"
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Switch Infrastructure Configuration
    # Uses sandbox-quantum/switch agent protocol:
    # 1. Registration via POST /agents (with AGENT_REGISTRATION_TOKEN) -> yields agent id & secret
    # 2. SSE Inbound Stream via GET /agents/{id}/events
    # 3. Connection Heartbeat via POST /agents/{id}/connection/beat (every 5-10s)
    # 4. Outbound Room Messaging via POST /rooms/{room_id}/messages
    SWITCH_URL: str = os.getenv("SWITCH_URL", "http://localhost:8000/switch/api")
    AGENT_REGISTRATION_TOKEN: str = os.getenv("AGENT_REGISTRATION_TOKEN", "switch_ideaflow_token_2026")
    AGENT_NAME: str = "IdeaFlow Agent"
    AGENT_ID: str = os.getenv("AGENT_ID", "agent_ideaflow_creative_01")
    AGENT_SECRET: str = os.getenv("AGENT_SECRET", "sec_ideaflow_switch_7749")
    SWITCH_ROOM_ID: str = os.getenv("SWITCH_ROOM_ID", "room_discord_nature_channel")
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
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    BUILTIN_SWITCH_ENABLED: bool = True

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
