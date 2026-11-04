import asyncio
import json
import logging
import uuid
import httpx
from datetime import datetime, timezone
from typing import Optional, Callable, Dict, Any
from backend.config import settings
from backend.database import SessionLocal, SwitchEventLog

logger = logging.getLogger("switch_client")

class SwitchAgentClient:
    def __init__(self):
        self.switch_url = settings.SWITCH_URL
        self.agent_id = settings.AGENT_ID
        self.agent_secret = settings.AGENT_SECRET
        self.connection_model = settings.CONNECTION_MODEL
        self.connection_id = f"conn_{uuid.uuid4().hex[:8]}"
        self.cursor = 0
        self.is_connected = False
        self.is_running = False
        self.event_handler: Optional[Callable[[Dict[str, Any]], Any]] = None
        self._beat_task: Optional[asyncio.Task] = None
        self._sse_task: Optional[asyncio.Task] = None
        self.last_beat_time: Optional[datetime] = None
        self.total_events_received: int = 0
        self.total_messages_sent: int = 0

    @property
    def is_builtin_hub(self) -> bool:
        return "/switch/api" in self.switch_url

    def set_event_handler(self, handler: Callable[[Dict[str, Any]], Any]):
        self.event_handler = handler

    def log_event(self, event_type: str, direction: str, payload: Any, room_id: Optional[str] = None):
        """Persists protocol frames to database for the Switch Protocol Inspector."""
        try:
            db = SessionLocal()
            log = SwitchEventLog(
                event_type=event_type,
                direction=direction,
                cursor=self.cursor,
                room_id=room_id or settings.SWITCH_ROOM_ID,
                payload=json.dumps(payload) if isinstance(payload, (dict, list)) else str(payload)
            )
            db.add(log)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to log Switch event: {e}")

    async def register(self) -> bool:
        """
        Switch Agent Protocol: Registration
        POST {SWITCH_URL}/agents
        """
        if self.is_builtin_hub:
            from backend.switch_hub import switch_state
            switch_state.registered_agents[self.agent_id] = {
                "id": self.agent_id,
                "name": settings.AGENT_NAME,
                "secret": self.agent_secret,
                "connection_model": self.connection_model,
                "status": "connected",
                "last_beat": datetime.now(timezone.utc).isoformat(),
                "cursor": self.cursor,
                "connection_id": self.connection_id
            }
            self.is_connected = True
            logger.info(f"Registered with Built-in Switch Hub: agent_id={self.agent_id}")
            self.log_event("agent_registered", "OUTBOUND", {
                "id": self.agent_id,
                "name": settings.AGENT_NAME,
                "model": self.connection_model,
                "hub": "builtin"
            })
            return True

        # Network registration against External Switch Server
        url = f"{self.switch_url}/agents"
        headers = {
            "Authorization": f"Bearer {settings.AGENT_REGISTRATION_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": settings.AGENT_NAME,
            "connection_model": self.connection_model,
            "description": "IdeaFlow AI Personal Creative Project Assistant"
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code in (200, 201):
                    data = res.json()
                    self.agent_id = data.get("id", self.agent_id)
                    self.agent_secret = data.get("secret", self.agent_secret)
                    self.is_connected = True
                    logger.info(f"Registered with External Switch: agent_id={self.agent_id}")
                    self.log_event("agent_registered", "OUTBOUND", data)
                    return True
                else:
                    logger.warning(f"External Switch registration returned {res.status_code}: {res.text}")
                    return False
        except Exception as e:
            logger.warning(f"Could not connect to external Switch server at {url}: {e}")
            return False

    async def send_beat(self) -> bool:
        """
        Switch Agent Protocol: Heartbeat
        POST {SWITCH_URL}/agents/{agent_id}/connection/beat
        """
        self.last_beat_time = datetime.now(timezone.utc)
        payload = {
            "connection_id": self.connection_id,
            "cursor": self.cursor
        }

        if self.is_builtin_hub:
            from backend.switch_hub import switch_state
            if self.agent_id in switch_state.registered_agents:
                agent = switch_state.registered_agents[self.agent_id]
                agent["last_beat"] = self.last_beat_time.isoformat()
                agent["cursor"] = self.cursor
                agent["status"] = "connected"
                agent["connection_id"] = self.connection_id
            self.log_event("connection_beat", "OUTBOUND", payload)
            return True

        url = f"{self.switch_url}/agents/{self.agent_id}/connection/beat"
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    self.log_event("connection_beat", "OUTBOUND", payload)
                    return True
                elif res.status_code in (404, 409):
                    logger.warning("Beat rejected (404/409): re-registering stream")
                    await self.register()
                    return False
        except Exception as e:
            logger.debug(f"External beat failed: {e}")
            return False
        return False

    async def start_heartbeat_loop(self):
        """Maintains heartbeat every 8 seconds per Switch protocol specification."""
        while self.is_running:
            try:
                await self.send_beat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Heartbeat loop exception: {e}")
            await asyncio.sleep(8)

    async def start_sse_listener(self):
        """
        Switch Agent Protocol: Persistent Server-Sent Events (SSE) Stream
        GET {SWITCH_URL}/agents/{agent_id}/events?connection_id={uuid}&cursor={cursor}
        """
        if self.is_builtin_hub:
            # Internal direct queue listener for the embedded Switch hub
            from backend.switch_hub import switch_state
            queue_key = f"{self.agent_id}:{self.connection_id}"
            q = asyncio.Queue()
            switch_state.event_queues[queue_key] = q
            switch_state.active_connections[queue_key] = {
                "agent_id": self.agent_id,
                "connection_id": self.connection_id,
                "connected_at": datetime.now(timezone.utc).isoformat()
            }
            self.is_connected = True
            self.log_event("sse_connected", "INBOUND", {"hub": "builtin", "connection_id": self.connection_id})

            try:
                while self.is_running:
                    try:
                        frame = await asyncio.wait_for(q.get(), timeout=12.0)
                        event_type = frame.get("event", "message")
                        self.cursor = int(frame.get("id", self.cursor + 1))
                        payload = json.loads(frame.get("data", "{}"))
                        self.total_events_received += 1

                        if event_type != "ping":
                            self.log_event(f"sse_{event_type}", "INBOUND", payload, payload.get("room_id"))

                        if self.event_handler and event_type in ("message", "task", "project_request"):
                            asyncio.create_task(self.event_handler(payload))
                    except asyncio.TimeoutError:
                        pass
            finally:
                if queue_key in switch_state.event_queues:
                    del switch_state.event_queues[queue_key]
                if queue_key in switch_state.active_connections:
                    del switch_state.active_connections[queue_key]
            return

        # External Switch Server SSE network stream
        while self.is_running:
            url = f"{self.switch_url}/agents/{self.agent_id}/events"
            params = {
                "connection_id": self.connection_id,
                "cursor": self.cursor
            }
            headers = {
                "Authorization": f"Bearer {self.agent_secret}",
                "Accept": "text/event-stream"
            }
            try:
                logger.info(f"Opening External Switch SSE stream at {url}...")
                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream("GET", url, params=params, headers=headers) as response:
                        if response.status_code != 200:
                            logger.warning(f"External Switch SSE failed with status {response.status_code}")
                            self.is_connected = False
                            await asyncio.sleep(4)
                            continue

                        self.is_connected = True
                        logger.info("Connected to External Switch SSE stream!")
                        self.log_event("sse_connected", "INBOUND", {"hub": "external", "connection_id": self.connection_id})

                        event_type = "message"
                        async for line in response.aiter_lines():
                            if not self.is_running:
                                break
                            line = line.strip()
                            if not line:
                                continue
                            if line.startswith("event:"):
                                event_type = line[6:].strip()
                            elif line.startswith("id:"):
                                try:
                                    self.cursor = int(line[3:].strip())
                                except Exception:
                                    pass
                            elif line.startswith("data:"):
                                data_str = line[5:].strip()
                                try:
                                    payload = json.loads(data_str)
                                    self.total_events_received += 1
                                    if "cursor" in payload:
                                        self.cursor = max(self.cursor, payload["cursor"])

                                    if event_type != "ping":
                                        self.log_event(f"sse_{event_type}", "INBOUND", payload, payload.get("room_id"))

                                    if self.event_handler and event_type in ("message", "task", "project_request"):
                                        asyncio.create_task(self.event_handler(payload))
                                except Exception as err:
                                    logger.error(f"Error handling SSE payload: {err}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.is_connected = False
                logger.debug(f"External Switch SSE disconnected: {e}. Retrying in 4s...")
                await asyncio.sleep(4)

    async def post_human_message_to_switch(
        self,
        room_id: str,
        content: str,
        sender: str = "Alex (Creator)",
        platform: str = "discord",
        channel_id: Optional[str] = None,
        discord_message_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> bool:
        """
        Dispatches a human message (from real Discord or simulator) into Switch Room
        POST {SWITCH_URL}/rooms/{room_id}/messages
        """
        payload = {
            "content": content,
            "sender": sender,
            "sender_type": "human",
            "platform": platform,
            "channel_id": channel_id,
            "discord_message_id": discord_message_id,
            "thread_id": thread_id,
            "is_agent_mention": True
        }

        if self.is_builtin_hub:
            from backend.switch_hub import post_room_message
            await post_room_message(room_id, payload)
            self.log_event("human_message_to_switch", "INBOUND", payload, room_id)
            return True

        url = f"{self.switch_url}/rooms/{room_id}/messages"
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code in (200, 201):
                    self.log_event("human_message_to_switch", "INBOUND", payload, room_id)
                    return True
        except Exception as e:
            logger.error(f"Failed to post human message to external Switch: {e}")
            return False
        return False

    async def post_room_message(
        self,
        room_id: str,
        content: str,
        sender_type: str = "agent",
        sender: str = "IdeaFlow Agent",
        thread_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        channel_id: Optional[str] = None
    ) -> bool:
        """
        Switch Agent Protocol: Outbound Room Messaging
        POST {SWITCH_URL}/rooms/{room_id}/messages
        """
        payload = {
            "content": content,
            "sender": sender,
            "sender_type": sender_type,
            "platform": "discord",
            "thread_id": thread_id,
            "reply_to": reply_to,
            "channel_id": channel_id
        }

        if self.is_builtin_hub:
            from backend.switch_hub import post_room_message
            await post_room_message(room_id, payload)
            self.total_messages_sent += 1
            self.log_event("room_message_outbound", "OUTBOUND", payload, room_id)
            return True

        url = f"{self.switch_url}/rooms/{room_id}/messages"
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code in (200, 201):
                    self.total_messages_sent += 1
                    self.log_event("room_message_outbound", "OUTBOUND", payload, room_id)
                    return True
                else:
                    logger.warning(f"Post room message returned {res.status_code}: {res.text}")
                    return False
        except Exception as e:
            logger.error(f"Failed to post room message to external Switch: {e}")
            return False

    async def start(self):
        """Starts the Switch agent lifecycle: registration, SSE stream, and heartbeat loop."""
        self.is_running = True
        logger.info(f"Starting Switch Agent Protocol client (Hub: {'Built-in' if self.is_builtin_hub else 'External'})...")
        
        # 1. Register with Switch
        await self.register()

        # 2. Start SSE listener and Heartbeat loops
        self._sse_task = asyncio.create_task(self.start_sse_listener())
        self._beat_task = asyncio.create_task(self.start_heartbeat_loop())

    async def stop(self):
        self.is_running = False
        self.is_connected = False
        if self._beat_task:
            self._beat_task.cancel()
        if self._sse_task:
            self._sse_task.cancel()
        logger.info("Stopped Switch Agent Protocol client.")

switch_client = SwitchAgentClient()
