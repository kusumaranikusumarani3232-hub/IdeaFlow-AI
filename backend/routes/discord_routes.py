from fastapi import APIRouter
from typing import Dict, Any
from backend.discord_bridge import discord_bridge
from backend.switch_hub import broadcast_switch_event
from backend.models import DiscordSimulateMessage
from backend.config import settings

router = APIRouter(prefix="/api/discord", tags=["Discord Bridge"])

@router.get("/status")
def get_discord_status():
    """Returns real Discord Gateway bot status."""
    return discord_bridge.get_status()

@router.post("/simulate")
async def simulate_discord_message(data: DiscordSimulateMessage):
    """
    Simulates a message sent by a human user in Discord.
    Dispatches directly into the Switch room event stream, demonstrating
    the complete Discord -> Switch -> IdeaFlow Agent -> Project updates loop.
    """
    room_id = settings.SWITCH_ROOM_ID
    event_payload = {
        "type": "room.message",
        "room_id": room_id,
        "message_id": f"sim_discord_{int(data.content.__hash__() & 0xfffffff)}",
        "sender": data.author,
        "sender_type": "human",
        "content": data.content,
        "platform": "discord",
        "channel_name": data.channel_name,
        "thread_id": data.thread_id,
        "is_agent_mention": data.is_agent_mention,
        "is_simulated": True
    }
    
    # Broadcast to Switch room SSE stream
    await broadcast_switch_event("message", event_payload)

    return {
        "status": "relayed_to_switch",
        "room_id": room_id,
        "sender": data.author,
        "content": data.content,
        "channel": data.channel_name,
        "protocol_action": "Dispatched to Switch SSE event queue"
    }
