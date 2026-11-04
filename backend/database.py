import json
import uuid
from datetime import datetime, timezone
from typing import Generator
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

DATABASE_URL = "sqlite:///./ideaflow.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_utc_now():
    return datetime.now(timezone.utc)

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    concept = Column(Text, nullable=False)
    category = Column(String, default="video")  # video, podcast, book, game, brand, creative
    status = Column(String, default="planning")  # planning, in_progress, review, completed
    progress = Column(Integer, default=15)       # 0 - 100
    target_audience = Column(Text, nullable=True)
    visual_identity = Column(Text, nullable=True)
    content_roadmap = Column(Text, nullable=True)  # JSON string
    summary = Column(Text, nullable=True)
    discord_channel_id = Column(String, nullable=True)
    switch_room_id = Column(String, default="room_discord_nature_channel")
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="project", cascade="all, delete-orphan")
    drafts = relationship("CreativeDraft", back_populates="project", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self):
        roadmap_parsed = []
        if self.content_roadmap:
            try:
                roadmap_parsed = json.loads(self.content_roadmap)
            except Exception:
                roadmap_parsed = [self.content_roadmap]
        return {
            "id": self.id,
            "title": self.title,
            "concept": self.concept,
            "category": self.category,
            "status": self.status,
            "progress": self.progress,
            "target_audience": self.target_audience,
            "visual_identity": self.visual_identity,
            "content_roadmap": roadmap_parsed,
            "summary": self.summary,
            "discord_channel_id": self.discord_channel_id,
            "switch_room_id": self.switch_room_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "task_count": len(self.tasks) if self.tasks else 0,
            "decision_count": len(self.decisions) if self.decisions else 0,
            "draft_count": len(self.drafts) if self.drafts else 0,
        }

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="todo")        # todo, in_progress, review, done
    priority = Column(String, default="medium")    # high, medium, low
    category = Column(String, default="pre-production")  # pre-production, production, post-production, branding, distribution
    assigned_to = Column(String, default="IdeaFlow Agent")  # Human, IdeaFlow Agent, Collaborative
    due_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "category": self.category,
            "assigned_to": self.assigned_to,
            "due_date": self.due_date,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    decision = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    category = Column(String, default="Identity")  # Identity, Content, Schedule, Equipment, Platform
    decided_by = Column(String, default="Consensus") # Human, IdeaFlow Agent, Consensus
    created_at = Column(DateTime, default=get_utc_now)

    project = relationship("Project", back_populates="decisions")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "decision": self.decision,
            "rationale": self.rationale,
            "category": self.category,
            "decided_by": self.decided_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class CreativeDraft(Base):
    __tablename__ = "creative_drafts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    draft_type = Column(String, default="script")  # script, pitch_deck, outline, copy, brand_identity
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    project = relationship("Project", back_populates="drafts")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "draft_type": self.draft_type,
            "content": self.content,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class SwitchEventLog(Base):
    __tablename__ = "switch_event_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=get_utc_now)
    event_type = Column(String, nullable=False)  # register, sse_inbound, beat, outbound_post, message, discord_bridge
    direction = Column(String, default="INBOUND") # INBOUND, OUTBOUND, INTERNAL
    cursor = Column(Integer, default=0)
    room_id = Column(String, nullable=True)
    payload = Column(Text, nullable=True)

    def to_dict(self):
        parsed_payload = self.payload
        try:
            parsed_payload = json.loads(self.payload)
        except Exception:
            pass
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_type": self.event_type,
            "direction": self.direction,
            "cursor": self.cursor,
            "room_id": self.room_id,
            "payload": parsed_payload,
        }

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    sender_type = Column(String, default="human")  # human, agent, system
    sender_name = Column(String, default="Alex (Creator)")
    content = Column(Text, nullable=False)
    platform = Column(String, default="discord")   # discord, switch, web
    discord_message_id = Column(String, nullable=True)
    discord_thread_id = Column(String, nullable=True)
    switch_event_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    project = relationship("Project", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "sender_type": self.sender_type,
            "sender_name": self.sender_name,
            "content": self.content,
            "platform": self.platform,
            "discord_message_id": self.discord_message_id,
            "discord_thread_id": self.discord_thread_id,
            "switch_event_id": self.switch_event_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

def init_db():
    Base.metadata.create_all(bind=engine)

# Auto-initialize SQLite tables on load
init_db()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

