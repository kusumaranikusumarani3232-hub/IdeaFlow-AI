from fastapi import APIRouter
from typing import Dict, Any
from backend.discord_bridge import discord_bridge
from backend.switch_client import switch_client
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
    Dispatches directly into the Switch room message endpoint over the official protocol,
    triggering the complete Discord -> Switch -> IdeaFlow Agent -> Project updates loop.
    """
    room_id = settings.SWITCH_ROOM_ID
    channel_id = settings.DISCORD_CHANNEL_ID or "123456789012345678"
    msg_id = f"sim_discord_{abs(hash(data.content)) % 10000000}"

    await switch_client.post_human_message_to_switch(
        room_id=room_id,
        content=data.content,
        sender=data.author,
        platform="discord",
        channel_id=channel_id,
        discord_message_id=msg_id,
        thread_id=data.thread_id
    )

    return {
        "status": "relayed_to_switch",
        "room_id": room_id,
        "sender": data.author,
        "content": data.content,
        "channel": data.channel_name,
        "protocol_action": "Dispatched to Switch room message endpoint"
    }
