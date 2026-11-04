import asyncio
import logging
from typing import Optional, Dict, Any
import discord
from backend.config import settings
from backend.switch_hub import switch_state, broadcast_switch_event

logger = logging.getLogger("discord_bridge")

class DiscordBridge:
    def __init__(self):
        self.bot_token = settings.DISCORD_BOT_TOKEN
        self.channel_id = settings.DISCORD_CHANNEL_ID
        self.guild_id = settings.DISCORD_GUILD_ID
        self.client: Optional[discord.Client] = None
        self.is_connected = False
        self.bot_user: Optional[str] = None
        self.status_message = "Not configured"
        self._bot_task: Optional[asyncio.Task] = None

    def get_status(self) -> Dict[str, Any]:
        return {
            "configured": bool(self.bot_token),
            "is_connected": self.is_connected,
            "bot_user": self.bot_user,
            "channel_id": self.channel_id,
            "guild_id": self.guild_id,
            "status_message": self.status_message,
            "mode": "live_gateway" if self.is_connected else "standby_or_simulated"
        }

    async def start(self):
        if not self.bot_token:
            self.status_message = "Standby (No DISCORD_BOT_TOKEN set in .env)"
            logger.info("Discord bridge in standby mode: DISCORD_BOT_TOKEN not provided.")
            return

        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready():
            self.is_connected = True
            self.bot_user = str(self.client.user)
            self.status_message = f"Connected as {self.bot_user}"
            logger.info(f"Discord Bot logged in as {self.bot_user} (ID: {self.client.user.id})")

        @self.client.event
        async def on_message(message: discord.Message):
            # Ignore messages sent by the bot itself
            if message.author == self.client.user:
                return

            # Check if relevant (channel matches, or bot mentioned, or DM)
            is_mention = self.client.user in message.mentions if self.client.user else False
            is_relevant_channel = not self.channel_id or str(message.channel.id) == str(self.channel_id)

            if is_mention or is_relevant_channel:
                logger.info(f"Relaying Discord message from {message.author.name} to Switch Room...")
                
                # Clean content (strip bot mention tag if needed)
                content = message.content
                if self.client.user:
                    content = content.replace(f"<@{self.client.user.id}>", "@IdeaFlow").strip()

                # Dispatch frame into Switch room
                room_id = settings.SWITCH_ROOM_ID
                thread_id = str(message.channel.id) if isinstance(message.channel, discord.Thread) else None

                event_payload = {
                    "type": "room.message",
                    "room_id": room_id,
                    "message_id": f"discord_{message.id}",
                    "sender": message.author.display_name or message.author.name,
                    "sender_type": "human",
                    "content": content,
                    "platform": "discord",
                    "thread_id": thread_id,
                    "discord_message_id": str(message.id),
                    "channel_id": str(message.channel.id),
                    "is_agent_mention": True
                }
                
                # Broadcast into Switch event bus
                await broadcast_switch_event("message", event_payload)

        try:
            self._bot_task = asyncio.create_task(self.client.start(self.bot_token))
        except Exception as e:
            self.status_message = f"Discord start failed: {e}"
            logger.error(f"Failed to start Discord bot: {e}")

    async def send_discord_reply(self, channel_id: str, content: str, reply_to_id: Optional[str] = None):
        """Sends a message back into Discord channel/thread."""
        if not self.is_connected or not self.client:
            logger.debug("Cannot send Discord reply: Bot not connected.")
            return False

        try:
            channel = self.client.get_channel(int(channel_id))
            if not channel:
                channel = await self.client.fetch_channel(int(channel_id))
            
            if channel:
                if reply_to_id:
                    try:
                        ref_msg = await channel.fetch_message(int(reply_to_id))
                        await ref_msg.reply(content)
                        return True
                    except Exception:
                        pass
                await channel.send(content)
                return True
        except Exception as e:
            logger.error(f"Failed to post to Discord: {e}")
            return False
        return False

    async def stop(self):
        if self.client and not self.client.is_closed():
            await self.client.close()
        self.is_connected = False
        self.status_message = "Stopped"

discord_bridge = DiscordBridge()
