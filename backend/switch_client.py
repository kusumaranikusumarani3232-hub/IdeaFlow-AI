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
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code in (200, 201):
                    data = res.json()
                    self.agent_id = data.get("id", self.agent_id)
                    self.agent_secret = data.get("secret", self.agent_secret)
                    logger.info(f"Registered with Switch: agent_id={self.agent_id}")
                    self.log_event("agent_registered", "OUTBOUND", data)
                    return True
                else:
                    logger.warning(f"Switch registration returned {res.status_code}: {res.text}")
                    return False
        except Exception as e:
            logger.warning(f"Could not connect to external Switch server at {url}: {e}")
            return False

    async def send_beat(self) -> bool:
        """
        Switch Agent Protocol: Heartbeat
        POST {SWITCH_URL}/agents/{agent_id}/connection/beat
        """
        url = f"{self.switch_url}/agents/{self.agent_id}/connection/beat"
        payload = {
            "connection_id": self.connection_id,
            "cursor": self.cursor
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    self.last_beat_time = datetime.now(timezone.utc)
                    self.log_event("connection_beat", "OUTBOUND", payload)
                    return True
                elif res.status_code in (404, 409):
                    logger.warning("Beat rejected (404/409): reconnecting SSE stream")
                    return False
        except Exception as e:
            logger.debug(f"Beat failed: {e}")
            return False
        return False

    async def start_heartbeat_loop(self):
        """Maintains heartbeat every 8 seconds per Switch protocol recommendation."""
        while self.is_running:
            try:
                success = await self.send_beat()
                if not success and self.is_connected:
                    # Retry registration/stream if beat dropped
                    pass
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
                logger.info(f"Opening Switch SSE stream at {url}...")
                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream("GET", url, params=params, headers=headers) as response:
                        if response.status_code != 200:
                            logger.warning(f"Switch SSE failed with status {response.status_code}")
                            await asyncio.sleep(3)
                            continue

                        self.is_connected = True
                        logger.info("Connected to Switch SSE stream!")
                        self.log_event("sse_connected", "INBOUND", {"status": "connected", "connection_id": self.connection_id})

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
                                    
                                    # Update cursor if provided
                                    if "cursor" in payload:
                                        self.cursor = max(self.cursor, payload["cursor"])

                                    if event_type != "ping":
                                        self.log_event(f"sse_{event_type}", "INBOUND", payload, payload.get("room_id"))
                                    
                                    # Dispatch to agent handler
                                    if self.event_handler and event_type in ("message", "task", "project_request"):
                                        asyncio.create_task(self.event_handler(payload))
                                except Exception as err:
                                    logger.error(f"Error handling SSE payload: {err}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.is_connected = False
                logger.debug(f"Switch SSE connection disconnected: {e}. Reconnecting in 3s...")
                await asyncio.sleep(3)

    async def post_room_message(
        self,
        room_id: str,
        content: str,
        sender_type: str = "agent",
        sender: str = "IdeaFlow Agent",
        thread_id: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> bool:
        """
        Switch Agent Protocol: Outbound Room Messaging
        POST {SWITCH_URL}/rooms/{room_id}/messages
        """
        url = f"{self.switch_url}/rooms/{room_id}/messages"
        payload = {
            "content": content,
            "sender": sender,
            "sender_type": sender_type,
            "platform": "discord",
            "thread_id": thread_id,
            "reply_to": reply_to
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code in (200, 201):
                    self.total_messages_sent += 1
                    self.log_event("room_message_outbound", "OUTBOUND", payload, room_id)
                    return True
                else:
                    logger.warning(f"Post room message returned {res.status_code}: {res.text}")
                    return False
        except Exception as e:
            logger.error(f"Failed to post room message to Switch: {e}")
            return False

    async def start(self):
        """Starts the Switch agent lifecycle: registration, SSE stream, and heartbeat loop."""
        self.is_running = True
        logger.info("Starting Switch Agent Protocol client...")
        
        # 1. Attempt registration
        await self.register()

        # 2. Start SSE listener and Heartbeat tasks
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
