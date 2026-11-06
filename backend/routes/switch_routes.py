from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from backend.database import get_db, SwitchEventLog
from backend.switch_hub import switch_state
from backend.switch_client import switch_client
from backend.discord_bridge import discord_bridge
from backend.ai_agent import ai_agent
from backend.config import settings

router = APIRouter(prefix="/api/switch", tags=["Switch Inspector"])

@router.get("/status")
def get_switch_bridge_status():
    """Live status of Switch Agent Protocol integration."""
    is_builtin = switch_client.is_builtin_hub
    mode_label = "Built-in Switch Hub (Development Mode)" if is_builtin else "Official Switch Server (switch-core v0.31.0)"
    
    # Calculate live connection status based on active stream, generation fence, and recent beat
    if is_builtin:
        is_connected = switch_client.is_connected
    else:
        beat_alive = False
        if switch_client.last_beat_time:
            beat_age = (datetime.now(timezone.utc) - switch_client.last_beat_time).total_seconds()
            if beat_age < 15.0:
                beat_alive = True

        is_connected = bool(
            switch_client.is_running and
            switch_client.agent_id and
            switch_client.generation is not None and
            (switch_client.is_connected or beat_alive)
        )
    
    return {
        "switch_url": settings.SWITCH_URL,
        "mode": "builtin_hub" if is_builtin else "external_server",
        "mode_label": mode_label,
        "is_builtin": is_builtin,
        "agent_name": settings.AGENT_DISPLAY_NAME,
        "agent_id": switch_client.agent_id,
        "connection_model": switch_client.connection_model,
        "connection_id": switch_client.connection_id,
        "generation": switch_client.generation,
        "is_connected": is_connected,
        "is_running": switch_client.is_running,
        "cursor": switch_client.cursor,
        "total_events_received": switch_client.total_events_received,
        "total_messages_sent": switch_client.total_messages_sent,
        "last_beat_time": switch_client.last_beat_time.isoformat() if switch_client.last_beat_time else None,
        "room_id": switch_client.room_id or settings.SWITCH_ROOM_ID,
        "protocol": "Official Switch Agent Protocol v9 (SSE Inbound + HTTP Outbound)",
        "demo_mode": settings.DEMO_MODE if is_builtin else False,
        "error_message": switch_client.error_message,
        "ai_provider": ai_agent.provider,
        "has_gemini_key": bool(ai_agent.gemini_key),
        "has_openai_key": bool(ai_agent.openai_key),
        "has_discord_token": bool(discord_bridge.bot_token)
    }

@router.get("/events")
def get_switch_events(limit: int = 50, db: Session = Depends(get_db)):
    """Fetch Switch protocol event logs for live inspector."""
    logs = (
        db.query(SwitchEventLog)
        .order_by(SwitchEventLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [l.to_dict() for l in logs]

@router.post("/beat")
async def trigger_manual_beat():
    """Allows manual trigger of a Switch connection heartbeat."""
    success = await switch_client.send_beat()
    return {
        "success": success,
        "connection_id": switch_client.connection_id,
        "generation": switch_client.generation,
        "cursor": switch_client.cursor,
        "timestamp": switch_client.last_beat_time.isoformat() if switch_client.last_beat_time else None
    }

@router.post("/config")
async def update_runtime_config(payload: Dict[str, Any]):
    """Dynamically updates runtime connection config (Switch URL, Keys, Bot Token)."""
    switch_url = payload.get("switch_url")
    discord_token = payload.get("discord_token")
    channel_id = payload.get("channel_id")
    gemini_key = payload.get("gemini_key")
    openai_key = payload.get("openai_key")
    ai_provider = payload.get("ai_provider")
    demo_mode = payload.get("demo_mode")

    if switch_url is not None:
        settings.SWITCH_URL = switch_url
        switch_client.switch_url = switch_url
        # Re-register with the new target
        await switch_client.register()

    if demo_mode is not None:
        settings.DEMO_MODE = bool(demo_mode)

    if gemini_key is not None or openai_key is not None or ai_provider is not None:
        ai_agent.set_keys(gemini_key=gemini_key, openai_key=openai_key, provider=ai_provider)

    if discord_token is not None:
        settings.DISCORD_BOT_TOKEN = discord_token
        discord_bridge.bot_token = discord_token
        if channel_id:
            settings.DISCORD_CHANNEL_ID = channel_id
            discord_bridge.channel_id = channel_id
        if discord_token:
            await discord_bridge.start()

    return {
        "status": "updated",
        "switch_url": settings.SWITCH_URL,
        "is_builtin": switch_client.is_builtin_hub,
        "is_connected": switch_client.is_connected,
        "discord_status": discord_bridge.get_status()
    }
