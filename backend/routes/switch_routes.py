from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db, SwitchEventLog
from backend.switch_hub import switch_state
from backend.switch_client import switch_client
from backend.config import settings

router = APIRouter(prefix="/api/switch", tags=["Switch Inspector"])

@router.get("/status")
def get_switch_bridge_status():
    """Live status of Switch Agent Protocol integration."""
    return {
        "switch_url": settings.SWITCH_URL,
        "agent_name": settings.AGENT_NAME,
        "agent_id": switch_client.agent_id,
        "connection_model": switch_client.connection_model,
        "connection_id": switch_client.connection_id,
        "is_connected": switch_client.is_connected,
        "is_running": switch_client.is_running,
        "cursor": switch_client.cursor,
        "total_events_received": switch_client.total_events_received,
        "total_messages_sent": switch_client.total_messages_sent,
        "last_beat_time": switch_client.last_beat_time.isoformat() if switch_client.last_beat_time else None,
        "room_id": settings.SWITCH_ROOM_ID,
        "protocol": "Switch Agent Protocol (SSE Inbound + HTTP Outbound)",
        "builtin_hub_active": settings.BUILTIN_SWITCH_ENABLED,
        "demo_mode": settings.DEMO_MODE
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
        "cursor": switch_client.cursor,
        "timestamp": switch_client.last_beat_time.isoformat() if switch_client.last_beat_time else None
    }
