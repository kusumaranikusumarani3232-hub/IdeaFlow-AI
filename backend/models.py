from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ProjectCreate(BaseModel):
    title: str
    concept: str
    category: Optional[str] = "video"
    target_audience: Optional[str] = None
    visual_identity: Optional[str] = None
    discord_channel_id: Optional[str] = None
    switch_room_id: Optional[str] = "room_discord_nature_channel"

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    concept: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    target_audience: Optional[str] = None
    visual_identity: Optional[str] = None
    summary: Optional[str] = None
    content_roadmap: Optional[List[Dict[str, Any]]] = None

class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = "todo"
    priority: Optional[str] = "medium"
    category: Optional[str] = "pre-production"
    assigned_to: Optional[str] = "IdeaFlow Agent"
    due_date: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None

class DecisionCreate(BaseModel):
    project_id: str
    title: str
    decision: str
    rationale: Optional[str] = None
    category: Optional[str] = "Identity"
    decided_by: Optional[str] = "Consensus"

class DraftCreate(BaseModel):
    project_id: str
    title: str
    draft_type: Optional[str] = "script"
    content: str
    version: Optional[int] = 1

class DraftUpdate(BaseModel):
    title: Optional[str] = None
    draft_type: Optional[str] = None
    content: Optional[str] = None
    version: Optional[int] = None

class ChatMessageCreate(BaseModel):
    project_id: str
    content: str
    sender_name: Optional[str] = "Alex (Creator)"
    platform: Optional[str] = "discord"  # discord, switch, web
    discord_thread_id: Optional[str] = None

class SwitchRegisterRequest(BaseModel):
    name: str
    connection_model: str = "always_on"
    description: Optional[str] = None

class SwitchBeatRequest(BaseModel):
    connection_id: str
    cursor: int = 0

class SwitchOutboundMessage(BaseModel):
    room_id: str
    content: str
    thread_id: Optional[str] = None
    reply_to: Optional[str] = None

class AIGenerateRequest(BaseModel):
    project_id: str
    prompt: str
    context_type: Optional[str] = "creative" # roadmap, script, tasks, identity, review

class AIBrainstormRequest(BaseModel):
    concept: str
    category: Optional[str] = "video"
    vibe: Optional[str] = "Cinematic, inspiring, engaging"

class AIDecomposeRequest(BaseModel):
    project_id: str
    goal: str

class DiscordSimulateMessage(BaseModel):
    project_id: Optional[str] = None
    author: str = "Alex"
    channel_name: str = "#creative-lounge"
    content: str
    thread_id: Optional[str] = None
    is_agent_mention: bool = True

