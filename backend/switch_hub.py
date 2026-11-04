import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sse_starlette.sse import EventSourceResponse
from fastapi import APIRouter, HTTPException, Header, Query, Request

logger = logging.getLogger("switch_hub")

# In-memory Switch hub state
class SwitchHubState:
    def __init__(self):
        self.registered_agents: Dict[str, Dict[str, Any]] = {
            "agent_ideaflow_creative_01": {
                "id": "agent_ideaflow_creative_01",
                "name": "IdeaFlow Agent",
                "secret": "sec_ideaflow_switch_7749",
                "connection_model": "always_on",
                "status": "connected",
                "last_beat": datetime.now(timezone.utc).isoformat(),
                "cursor": 0,
                "connection_id": "conn_init_01"
            }
        }
        self.rooms: Dict[str, Dict[str, Any]] = {
            "room_discord_nature_channel": {
                "id": "room_discord_nature_channel",
                "name": "Nature & Wildlife Hub (Discord #creative-lounge)",
                "platform": "discord",
                "channel_id": "123456789012345678",
                "topic": "Collaborative project space for wildlife creative work",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        }
        self.messages: List[Dict[str, Any]] = []
        self.event_queues: Dict[str, asyncio.Queue] = {}
        self.cursor_counter: int = 1
        self.active_connections: Dict[str, Dict[str, Any]] = {}

switch_state = SwitchHubState()
switch_router = APIRouter(prefix="/switch/api", tags=["Switch Agent Protocol"])

@switch_router.get("/status")
async def get_switch_status():
    """Returns official Switch hub topology and active bridge telemetry."""
    active_agent_count = len(switch_state.registered_agents)
    connected_streams = len(switch_state.active_connections)
    return {
        "switch_version": "Switch Core 1.4.2 (Open-Source)",
        "protocol": "Switch Agent Protocol v1 (SSE Inbound + HTTP Outbound)",
        "status": "active",
        "registered_agents": list(switch_state.registered_agents.values()),
        "active_rooms": list(switch_state.rooms.values()),
        "active_connections_count": connected_streams,
        "total_messages": len(switch_state.messages),
        "last_cursor": switch_state.cursor_counter,
        "bridge_adapter": "discord_matrix_bridge",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@switch_router.post("/agents")
async def register_agent(
    payload: Dict[str, Any],
    authorization: Optional[str] = Header(None)
):
    """
    Switch Agent Protocol: Agent Registration
    POST /agents
    Auth: Bearer AGENT_REGISTRATION_TOKEN
    Body: {"name": "...", "connection_model": "always_on"}
    """
    token = ""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    
    agent_id = f"agent_{uuid.uuid4().hex[:8]}"
    agent_secret = f"sec_{uuid.uuid4().hex[:16]}"
    name = payload.get("name", "IdeaFlow Agent")
    conn_model = payload.get("connection_model", "always_on")

    agent_record = {
        "id": agent_id,
        "name": name,
        "secret": agent_secret,
        "connection_model": conn_model,
        "status": "registered",
        "last_beat": datetime.now(timezone.utc).isoformat(),
        "cursor": switch_state.cursor_counter,
        "connection_id": None
    }
    switch_state.registered_agents[agent_id] = agent_record
    
    logger.info(f"Registered agent {agent_id} ({name}) with model {conn_model}")
    return {
        "id": agent_id,
        "name": name,
        "secret": agent_secret,
        "connection_model": conn_model,
        "status": "registered",
        "protocol_version": "1.0"
    }

@switch_router.post("/agents/{agent_id}/connection/beat")
async def connection_beat(
    agent_id: str,
    payload: Dict[str, Any]
):
    """
    Switch Agent Protocol: Heartbeat (every 5-10s)
    POST /agents/{agent_id}/connection/beat
    Body: {"connection_id": "...", "cursor": 12}
    """
    if agent_id not in switch_state.registered_agents:
        raise HTTPException(status_code=404, detail="Agent connection not found or expired")
    
    conn_id = payload.get("connection_id", "default_conn")
    cursor = payload.get("cursor", switch_state.cursor_counter)
    
    agent = switch_state.registered_agents[agent_id]
    agent["last_beat"] = datetime.now(timezone.utc).isoformat()
    agent["cursor"] = cursor
    agent["connection_id"] = conn_id
    agent["status"] = "connected"

    return {
        "status": "ok",
        "agent_id": agent_id,
        "connection_id": conn_id,
        "cursor": cursor,
        "server_time": datetime.now(timezone.utc).isoformat()
    }

@switch_router.get("/agents/{agent_id}/events")
async def agent_events_sse(
    request: Request,
    agent_id: str,
    connection_id: Optional[str] = Query(None),
    cursor: Optional[int] = Query(0),
    authorization: Optional[str] = Header(None)
):
    """
    Switch Agent Protocol: Inbound Server-Sent Events (SSE) Stream
    GET /agents/{id}/events?connection_id=...&cursor=...
    Pushes messages, mentions, and tasks from Switch rooms down to the agent.
    """
    if agent_id not in switch_state.registered_agents:
        # Auto-register if using preset ID
        switch_state.registered_agents[agent_id] = {
            "id": agent_id,
            "name": "IdeaFlow Agent",
            "secret": "sec_auto",
            "connection_model": "always_on",
            "status": "connected",
            "last_beat": datetime.now(timezone.utc).isoformat(),
            "cursor": cursor or 0,
            "connection_id": connection_id or "conn_stream"
        }

    queue_key = f"{agent_id}:{connection_id or 'default'}"
    q = asyncio.Queue()
    switch_state.event_queues[queue_key] = q
    switch_state.active_connections[queue_key] = {
        "agent_id": agent_id,
        "connection_id": connection_id,
        "connected_at": datetime.now(timezone.utc).isoformat()
    }

    async def event_generator():
        try:
            # Yield initial connection confirmation frame
            init_frame = {
                "type": "switch.connected",
                "agent_id": agent_id,
                "connection_id": connection_id,
                "cursor": switch_state.cursor_counter,
                "rooms": list(switch_state.rooms.keys()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            yield {
                "event": "connection_ready",
                "id": str(switch_state.cursor_counter),
                "data": json.dumps(init_frame)
            }

            while True:
                if await request.is_disconnected():
                    logger.info(f"SSE client disconnected: {queue_key}")
                    break
                
                try:
                    # Wait for next event with a periodic keepalive ping
                    event = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield event
                except asyncio.TimeoutError:
                    # Keepalive ping frame
                    yield {
                        "event": "ping",
                        "data": json.dumps({
                            "type": "heartbeat",
                            "server_time": datetime.now(timezone.utc).isoformat()
                        })
                    }
        finally:
            if queue_key in switch_state.event_queues:
                del switch_state.event_queues[queue_key]
            if queue_key in switch_state.active_connections:
                del switch_state.active_connections[queue_key]

    return EventSourceResponse(event_generator())

async def broadcast_switch_event(event_type: str, data: Dict[str, Any]):
    """Dispatches a frame to all active agent SSE listeners."""
    switch_state.cursor_counter += 1
    frame_id = str(switch_state.cursor_counter)
    data["cursor"] = switch_state.cursor_counter
    data["event_id"] = f"evt_{switch_state.cursor_counter}"

    frame = {
        "event": event_type,
        "id": frame_id,
        "data": json.dumps(data)
    }

    for queue in list(switch_state.event_queues.values()):
        await queue.put(frame)

@switch_router.post("/rooms/{room_id}/messages")
async def post_room_message(
    room_id: str,
    payload: Dict[str, Any]
):
    """
    Switch Agent Protocol: Outbound message / Human incoming message
    POST /rooms/{room_id}/messages
    Body: {"content": "...", "sender": "...", "platform": "discord", "thread_id": "..."}
    """
    content = payload.get("content", "")
    sender = payload.get("sender", "Alex (Creator)")
    sender_type = payload.get("sender_type", "human") # human | agent | bot
    platform = payload.get("platform", "discord")
    thread_id = payload.get("thread_id", None)
    reply_to = payload.get("reply_to", None)

    msg_id = f"msg_{uuid.uuid4().hex[:10]}"
    message_record = {
        "id": msg_id,
        "room_id": room_id,
        "sender": sender,
        "sender_type": sender_type,
        "content": content,
        "platform": platform,
        "thread_id": thread_id,
        "reply_to": reply_to,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    switch_state.messages.append(message_record)

    # Broadcast event into Switch event stream for the agent
    event_payload = {
        "type": "room.message",
        "room_id": room_id,
        "message_id": msg_id,
        "sender": sender,
        "sender_type": sender_type,
        "content": content,
        "platform": platform,
        "thread_id": thread_id,
        "reply_to": reply_to,
        "is_agent_mention": ("@IdeaFlow" in content) or ("@ideaflow" in content.lower()) or (sender_type == "human")
    }
    await broadcast_switch_event("message", event_payload)

    return {
        "status": "delivered",
        "message": message_record,
        "cursor": switch_state.cursor_counter
    }

@switch_router.get("/rooms/{room_id}/messages")
async def get_room_messages(room_id: str):
    """Returns conversation history in the Switch room."""
    room_msgs = [m for m in switch_state.messages if m["room_id"] == room_id]
    return {
        "room_id": room_id,
        "messages": room_msgs,
        "count": len(room_msgs)
    }
