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
        self.api_key = settings.AGENT_SECRET
        self.agent_secret = settings.AGENT_SECRET
        self.room_id = settings.SWITCH_ROOM_ID
        self.connection_model = settings.CONNECTION_MODEL
        self.connection_id = f"conn_{uuid.uuid4().hex[:12]}"
        self.generation: Optional[int] = None
        self.cursor = 0
        self.is_connected = False
        self.is_running = False
        self.is_registered = False
        self.event_handler: Optional[Callable[[Dict[str, Any]], Any]] = None
        self._beat_task: Optional[asyncio.Task] = None
        self._sse_task: Optional[asyncio.Task] = None
        self.last_beat_time: Optional[datetime] = None
        self.total_events_received: int = 0
        self.total_messages_sent: int = 0
        self.error_message: Optional[str] = None

    @property
    def is_builtin_hub(self) -> bool:
        return "/switch/api" in self.switch_url

    def set_event_handler(self, handler: Callable[[Dict[str, Any]], Any]):
        self.event_handler = handler

    def log_event(self, event_type: str, direction: str, payload: Any, room_id: Optional[str] = None):
        """Persists protocol frames to SQLite database for the Switch Protocol Inspector."""
        try:
            db = SessionLocal()
            log = SwitchEventLog(
                event_type=event_type,
                direction=direction,
                cursor=self.cursor,
                room_id=room_id or self.room_id or settings.SWITCH_ROOM_ID,
                payload=json.dumps(payload) if isinstance(payload, (dict, list)) else str(payload)
            )
            db.add(log)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to log Switch event: {e}")

    async def _ensure_local_switch_running(self) -> bool:
        """Verifies official Switch server connectivity; auto-starts if local installation detected."""
        if self.is_builtin_hub:
            return True

        health_url = f"{self.switch_url}/health"
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(health_url)
                if res.status_code == 200:
                    return True
        except Exception:
            pass

        # Only auto-launch if targeting localhost/127.0.0.1
        if "127.0.0.1" in self.switch_url or "localhost" in self.switch_url:
            import os
            import sys
            import subprocess
            native_dir = r"C:\Users\kusuma\AppData\Roaming\switchdash\local-switch-server\native"
            script_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "switch_server_service.py"))
            if os.path.exists(native_dir) and os.path.exists(script_path):
                logger.info("Official Switch server offline. Auto-starting local Switch daemon...")
                try:
                    subprocess.Popen(
                        [sys.executable, script_path],
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                    for _ in range(16):
                        await asyncio.sleep(0.5)
                        try:
                            async with httpx.AsyncClient(timeout=1.0) as client:
                                r = await client.get(health_url)
                                if r.status_code == 200:
                                    logger.info("Local Switch Core service is now healthy and ready!")
                                    return True
                        except Exception:
                            pass
                except Exception as ex:
                    logger.warning(f"Could not auto-start local Switch daemon: {ex}")

        return False

    async def register(self) -> bool:
        """
        Switch Agent Protocol: Agent Registration
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
            self.is_registered = True
            self.error_message = None
            logger.info(f"Registered with Built-in Switch Hub: agent_id={self.agent_id}")
            self.log_event("agent_registered", "OUTBOUND", {
                "id": self.agent_id,
                "name": settings.AGENT_NAME,
                "model": self.connection_model,
                "hub": "builtin"
            })
            return True

        # Ensure server is running before attempting network registration
        await self._ensure_local_switch_running()

        # Network registration against Official Switch Server (switch-core v0.31.0)
        url = f"{self.switch_url}/agents"
        headers = {
            "Authorization": f"Bearer {settings.AGENT_REGISTRATION_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": settings.AGENT_NAME,
            "display_name": settings.AGENT_DISPLAY_NAME,
            "description": "Your Personal Creative Project Assistant",
            "connector_type": "custom",
            "integration_profile": {
                "connection_model": self.connection_model,
                "message_exchange": True,
                "pre_invocation_mediation": [],
                "post_invocation_mediation": [],
                "event_reporting": [],
                "command_capabilities": {
                    "reset": "unsupported",
                    "compact": "unsupported",
                    "interrupt": "unsupported"
                }
            },
            "tools": [],
            "models": [],
            "metadata": {"version": settings.VERSION},
            "overwrite": True
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code in (200, 201):
                    data = res.json()
                    self.agent_id = data.get("id", self.agent_id)
                    self.api_key = data.get("api_key", self.api_key)
                    self.agent_secret = self.api_key
                    self.is_registered = True
                    self.is_connected = True
                    self.error_message = None
                    logger.info(f"Registered with Official Switch Server: agent_id={self.agent_id}")

                    # Discover or create moderation room
                    await self._ensure_room(client)

                    self.log_event("agent_registered", "OUTBOUND", {
                        "id": self.agent_id,
                        "name": settings.AGENT_NAME,
                        "room_id": self.room_id,
                        "hub": "official_switch_core"
                    })
                    return True
                else:
                    self.error_message = f"Switch registration failed ({res.status_code}): {res.text}"
                    logger.warning(self.error_message)
                    self.is_connected = False
                    self.is_registered = False
                    return False
        except Exception as e:
            self.error_message = f"Could not connect to Switch server at {url}: {e}"
            logger.warning(self.error_message)
            self.is_connected = False
            self.is_registered = False
            return False

    async def _ensure_room(self, client: httpx.AsyncClient):
        """Discovers existing rooms or creates a dedicated moderation room for IdeaFlow AI."""
        if not self.agent_id or not self.api_key:
            return
        agent_headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            rooms_url = f"{self.switch_url}/agents/{self.agent_id}/moderation/rooms"
            res = await client.get(rooms_url, headers=agent_headers)
            if res.status_code == 200:
                rooms_data = res.json().get("rooms", [])
                if rooms_data:
                    self.room_id = rooms_data[0].get("id", self.room_id)
                    logger.info(f"Using existing Switch Room: id={self.room_id}, name={rooms_data[0].get('name')}")
                    return

            # No room found -> create room
            create_payload = {
                "name": "IdeaFlow Discord Room",
                "description": "Collaborative creative project room for IdeaFlow AI and Discord users",
                "agent_names": [settings.AGENT_NAME]
            }
            create_res = await client.post(rooms_url, json=create_payload, headers=agent_headers)
            if create_res.status_code in (200, 201):
                new_room = create_res.json()
                self.room_id = new_room.get("id", self.room_id)
                logger.info(f"Created dedicated Switch Room: id={self.room_id}")
        except Exception as err:
            logger.warning(f"Room discovery/creation encountered an error: {err}")

    async def send_beat(self) -> bool:
        """
        Switch Agent Protocol: Heartbeat Keep-Alive
        POST {SWITCH_URL}/agents/{agent_id}/connection/beat
        """
        if self.is_builtin_hub:
            self.last_beat_time = datetime.now(timezone.utc)
            from backend.switch_hub import switch_state
            if self.agent_id in switch_state.registered_agents:
                agent = switch_state.registered_agents[self.agent_id]
                agent["last_beat"] = self.last_beat_time.isoformat()
                agent["cursor"] = self.cursor
                agent["status"] = "connected"
                agent["connection_id"] = self.connection_id
            self.log_event("connection_beat", "OUTBOUND", {
                "connection_id": self.connection_id,
                "cursor": self.cursor,
                "hub": "builtin"
            })
            return True

        if not self.agent_id or not self.api_key:
            return False

        # Guard: Official Switch Core requires an active stream with valid generation fence
        if self.generation is None:
            return False

        url = f"{self.switch_url}/agents/{self.agent_id}/connection/beat"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "connection_id": self.connection_id,
            "generation": self.generation
        }

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    self.is_connected = True
                    self.last_beat_time = datetime.now(timezone.utc)
                    self.log_event("connection_beat", "OUTBOUND", {
                        "connection_id": self.connection_id,
                        "generation": self.generation,
                        "status": "ok",
                        "hub": "official_switch_core"
                    })
                    return True
                elif res.status_code in (404, 409):
                    logger.warning(f"Switch beat returned {res.status_code}: stream disconnected or generation expired.")
                    self.is_connected = False
                    self.generation = None
                    return False
        except Exception as e:
            logger.debug(f"External beat request failed: {e}")
            return False
        return False

    async def start_heartbeat_loop(self):
        """Maintains heartbeat every 2.5s (external) or 8s (built-in) per protocol spec."""
        interval = 2.5 if not self.is_builtin_hub else 8.0
        # Allow SSE listener initial handshake window before starting beats
        await asyncio.sleep(1.0)
        while self.is_running:
            try:
                if self.is_builtin_hub or self.generation is not None:
                    await self.send_beat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Heartbeat loop exception: {e}")
            await asyncio.sleep(interval)

    async def start_sse_listener(self):
        """
        Switch Agent Protocol: Persistent Server-Sent Events (SSE) Stream
        GET {SWITCH_URL}/agents/{agent_id}/events?connection_id={uuid}&scope=all&filter=all&rooms={room_id}
        """
        if self.is_builtin_hub:
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

        # Official External Switch Server SSE network stream
        while self.is_running:
            if not self.is_registered or not self.agent_id or not self.api_key:
                reg_ok = await self.register()
                if not reg_ok:
                    self.is_connected = False
                    await asyncio.sleep(3)
                    continue

            # Fresh connection parameters per connection attempt
            self.connection_id = f"conn_{uuid.uuid4().hex[:12]}"
            self.generation = None

            url = f"{self.switch_url}/agents/{self.agent_id}/events"
            params = {
                "connection_id": self.connection_id,
                "scope": "all",
                "filter": "all",
                "rooms": self.room_id or settings.SWITCH_ROOM_ID
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "text/event-stream"
            }
            try:
                logger.info(f"Connecting to Official Switch SSE stream at {url} (conn={self.connection_id})...")
                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream("GET", url, params=params, headers=headers) as response:
                        if response.status_code in (401, 403):
                            logger.warning(f"Switch SSE authentication rejected ({response.status_code}). Re-registering...")
                            self.is_registered = False
                            self.agent_id = None
                            self.api_key = None
                            self.is_connected = False
                            self.generation = None
                            await asyncio.sleep(2)
                            continue
                        elif response.status_code != 200:
                            logger.warning(f"Switch SSE failed with status {response.status_code}")
                            self.is_connected = False
                            self.generation = None
                            await asyncio.sleep(3)
                            continue

                        self.is_connected = True
                        logger.info("Connected to Official Switch SSE stream successfully!")

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

                                    if event_type == "connection_state":
                                        self.generation = payload.get("generation")
                                        self.cursor = payload.get("cursor", self.cursor)
                                        self.is_connected = True
                                        self.log_event("sse_connection_state", "INBOUND", payload, self.room_id)
                                    elif event_type != "ping":
                                        self.log_event(f"sse_{event_type}", "INBOUND", payload, payload.get("room_id") or self.room_id)

                                    # Handle inbound message events
                                    if event_type == "message":
                                        msg_p = payload.get("payload", {})
                                        body = msg_p.get("body") or payload.get("body") or payload.get("content")
                                        sender = msg_p.get("sender_name") or msg_p.get("sender") or payload.get("sender", "User")
                                        sender_kind = msg_p.get("sender_kind") or payload.get("sender_type")

                                        # Only trigger on non-agent messages to prevent self-echoes
                                        if sender_kind != "agent" and body and self.event_handler:
                                            asyncio.create_task(self.event_handler({
                                                "type": "room.message",
                                                "sender_type": "human",
                                                "sender": sender,
                                                "content": body,
                                                "room_id": payload.get("room_id") or self.room_id,
                                                "thread_id": msg_p.get("thread_id") or payload.get("thread_id"),
                                                "platform": "switch"
                                            }))
                                except Exception as err:
                                    logger.error(f"Error handling SSE payload: {err}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.is_connected = False
                self.generation = None
                logger.debug(f"Official Switch SSE disconnected: {e}. Reconnecting in 3s...")
                await asyncio.sleep(3)

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
        POST {SWITCH_URL}/agents/{agent_id}/message
        """
        target_room = room_id or self.room_id or settings.SWITCH_ROOM_ID

        if self.is_builtin_hub:
            from backend.switch_hub import post_room_message
            payload = {
                "content": content,
                "sender": sender,
                "sender_type": sender_type,
                "platform": "discord",
                "thread_id": thread_id,
                "reply_to": reply_to,
                "channel_id": channel_id
            }
            await post_room_message(target_room, payload)
            self.total_messages_sent += 1
            self.log_event("room_message_outbound", "OUTBOUND", payload, target_room)
            return True

        # Official Switch Server Outbound Messaging
        url = f"{self.switch_url}/agents/{self.agent_id}/message"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        body = {
            "room_id": target_room,
            "content": content
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(url, json=body, headers=headers)
                if res.status_code in (200, 201):
                    data = res.json()
                    event_id = data.get("event_id")
                    self.total_messages_sent += 1
                    self.log_event("room_message_outbound", "OUTBOUND", {
                        "room_id": target_room,
                        "content": content,
                        "event_id": event_id,
                        "server": "official_switch_core"
                    }, target_room)
                    return True
                else:
                    logger.warning(f"Post room message returned {res.status_code}: {res.text}")
                    return False
        except Exception as e:
            logger.error(f"Failed to post room message to official Switch: {e}")
            return False

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
        Dispatches a human message (from real Discord bot or simulator) into Switch Room workflow.
        """
        target_room = room_id or self.room_id or settings.SWITCH_ROOM_ID
        payload = {
            "content": content,
            "sender": sender,
            "sender_type": "human",
            "platform": platform,
            "channel_id": channel_id,
            "discord_message_id": discord_message_id,
            "thread_id": thread_id,
            "is_agent_mention": True,
            "room_id": target_room
        }

        self.log_event("human_message_to_switch", "INBOUND", payload, target_room)

        if self.is_builtin_hub:
            from backend.switch_hub import post_room_message
            await post_room_message(target_room, payload)
            return True

        # In External Switch Server mode, relay directly into agent processing loop
        if self.event_handler:
            asyncio.create_task(self.event_handler({
                "type": "room.message",
                "sender_type": "human",
                "sender": sender,
                "content": content,
                "platform": platform,
                "channel_id": channel_id,
                "discord_message_id": discord_message_id,
                "thread_id": thread_id,
                "room_id": target_room
            }))
        return True

    async def start(self):
        """Starts the Switch agent lifecycle: registration, room check, SSE stream, and heartbeat loop."""
        self.is_running = True
        logger.info(f"Starting Switch Agent Protocol client (Mode: {'Built-in Hub' if self.is_builtin_hub else 'Official External Server'})...")
        
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
