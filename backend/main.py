import asyncio
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import init_db, SessionLocal, Project, Task, Decision, CreativeDraft, ChatMessage
from backend.switch_hub import switch_router
from backend.switch_client import switch_client
from backend.discord_bridge import discord_bridge
from backend.ai_agent import ai_agent
from backend.routes import projects, switch_routes, discord_routes, ai_routes

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ideaflow_main")

def seed_demo_data():
    """Seeds the initial project (WildEcho – Nature & Wildlife Channel) if database is fresh."""
    db = SessionLocal()
    try:
        count = db.query(Project).count()
        if count == 0:
            logger.info("Database empty: seeding demo project 'WildEcho – Nature & Wildlife Channel'...")
            import json
            roadmap = [
                {"phase": "Pre-Production", "milestone": "Channel Identity & Visual Branding", "timeline": "Week 1", "status": "completed"},
                {"phase": "Production", "milestone": "Pilot Episode Filming (Urban Green Spaces)", "timeline": "Week 2-3", "status": "in_progress"},
                {"phase": "Post-Production", "milestone": "4K Color Grade & Binaural Sound Mixing", "timeline": "Week 4", "status": "pending"},
                {"phase": "Launch", "milestone": "Channel Launch & First 3 Videos Live", "timeline": "Week 5", "status": "pending"}
            ]

            proj = Project(
                id="proj_wildecho_nature_01",
                title="WildEcho - Nature & Wildlife Channel",
                concept="I want to launch a YouTube channel about nature and wildlife.",
                category="video",
                status="in_progress",
                progress=65,
                target_audience="Wildlife enthusiasts, slow-media documentary lovers, outdoor creators aged 18-45",
                visual_identity="Earth tones: Deep Forest Green (#1B4332), Warm Ochre (#DDA15E), Mist Grey (#E9ECEF). Atmospheric, cinematic, slow-panning 4K macro.",
                content_roadmap=json.dumps(roadmap),
                summary="A cinematic nature and wildlife documentary channel focusing on high-definition micro-habitats and immersive environmental storytelling.",
                switch_room_id=settings.SWITCH_ROOM_ID,
                discord_channel_id="123456789012345678"
            )

            db.add(proj)
            db.commit()

            # Seed Tasks
            tasks = [
                Task(
                    project_id=proj.id,
                    title="Establish Visual Identity & Brand Style Guide",
                    description="Select typography (cinematic serif + clean sans), color palette (forest green, stone grey), and channel banner artwork.",
                    category="branding",
                    priority="high",
                    status="done",
                    assigned_to="Collaborative"
                ),
                Task(
                    project_id=proj.id,
                    title="Write Episode 1 Script: 'Secrets of Urban Wilds'",
                    description="Complete full audio-visual screenplay including opening hook, micro-habitat sequences, and conservation takeaway.",
                    category="pre-production",
                    priority="high",
                    status="done",
                    assigned_to="IdeaFlow Agent"
                ),
                Task(
                    project_id=proj.id,
                    title="Field Equipment & Audio Setup Checklist",
                    description="Configure Sony A7SIII / FX3, 90mm Macro lens, Rode NTG5 shotgun mic, and wind protection for outdoor ambient recording.",
                    category="production",
                    priority="medium",
                    status="in_progress",
                    assigned_to="Alex (Creator)"
                ),
                Task(
                    project_id=proj.id,
                    title="Create Sound Design Template (Binaural Forest Foley)",
                    description="Build an audio preset bank with bird calls, wind rustle, stream ambiance, and sub-bass impact moments.",
                    category="post-production",
                    priority="medium",
                    status="todo",
                    assigned_to="IdeaFlow Agent"
                ),
                Task(
                    project_id=proj.id,
                    title="YouTube Channel Optimization & SEO Strategy",
                    description="Draft channel bio, 15 high-ranking tags (#wildlife, #naturedocumentary, #cinematicnature), and thumbnail templates with high-contrast text.",
                    category="distribution",
                    priority="medium",
                    status="todo",
                    assigned_to="Collaborative"
                )
            ]
            for t in tasks:
                db.add(t)

            # Seed Decisions
            decisions = [
                Decision(
                    project_id=proj.id,
                    title="Cinematic Documentary vs. Talking Head Vlog",
                    decision="Adopt a 100% immersive documentary narrative style with voiceover narration rather than on-camera talking head.",
                    rationale="Nature viewers prioritize visual immersion, sound design, and soothing narration over creator-centric drama.",
                    category="Identity",
                    decided_by="Consensus"
                ),
                Decision(
                    project_id=proj.id,
                    title="Bi-Weekly Release Schedule",
                    decision="Publish high-production episodes every two weeks on Sunday mornings at 9:00 AM EST.",
                    rationale="High-fidelity 4K nature cinematography requires extensive color grading and Foley mixing; bi-weekly ensures consistent quality.",
                    category="Schedule",
                    decided_by="Human"
                ),
                Decision(
                    project_id=proj.id,
                    title="Audio-First Production Philosophy",
                    decision="Invest equal time into sound design and natural Foley recording as visual capture.",
                    rationale="In nature videos, pristine 3D audio accounts for over 60% of viewer retention and emotional resonance.",
                    category="Content",
                    decided_by="IdeaFlow Agent"
                )
            ]
            for d in decisions:
                db.add(d)

            # Seed Creative Drafts
            pilot_script = (
                "# Episode 01: Secrets of the Urban Wilderness\n"
                "**Runtime:** 8-10 Minutes | **Pacing:** Atmospheric & Contemplative\n\n"
                "---\n\n"
                "### [00:00 - 00:30] Cold Open: The Invisible Jungle\n"
                "**[VISUAL - 4K Macro 120fps]:**\n"
                "Extreme close-up of a single blade of dew-covered grass in a city park. A solitary jumping spider (*Salticidae*) turns its iridescent eyes directly toward the lens.\n\n"
                "**[AUDIO]:**\n"
                "Distant, muffled city siren fades out. Crystal-clear sound of water drop dripping, crisp wind rustle, and high-frequency heartbeat pulse.\n\n"
                "**[NARRATION (Calm, grounding tone)]:**\n"
                "> \"We build concrete canyons to keep the wild at bay. But right beneath the pavement, under the flickering neon, life refuses to surrender. Welcome to the unseen wilderness... in our own backyards.\"\n\n"
                "---\n\n"
                "### [00:30 - 02:15] Sequence 1: The Canopy Above the Concrete\n"
                "**[VISUAL]:**\n"
                "Slow upward drone tilt from high-rise glass tower to a lush oak canopy nestled in an urban park. Cut to handheld telephoto of a red-tailed hawk nesting on an air conditioning unit.\n\n"
                "**[AUDIO]:**\n"
                "Binaural hawk cry echoed against stone walls. Soft, ambient acoustic guitar underscore begins.\n\n"
                "**[NARRATION]:**\n"
                "> \"Adaptation is not an accident—it is poetry in motion. Here, thirty floors above rush-hour traffic, an apex predator finds sanctuary.\"\n\n"
                "---\n\n"
                "### [02:15 - End Hook]\n"
                "**[PRODUCTION NOTES]:**\n"
                "- *Color Palette:* Grade with Kodak 2383 LUT emulation, emphasizing rich greens and warm morning sunlight.\n"
                "- *Deliverable:* Export master in 3840x2160 ProRes 422 HQ."
            )
            draft = CreativeDraft(
                project_id=proj.id,
                title="Episode 01 Pilot Script – 'Secrets of the Urban Wilderness'",
                draft_type="script",
                content=pilot_script,
                version=1
            )
            db.add(draft)

            # Seed Messages
            msg1 = ChatMessage(
                project_id=proj.id,
                sender_type="human",
                sender_name="Alex (Creator)",
                content="I want to launch a YouTube channel about nature and wildlife.",
                platform="discord"
            )
            msg2 = ChatMessage(
                project_id=proj.id,
                sender_type="agent",
                sender_name="IdeaFlow Agent",
                content=(
                    "🌿 **Welcome to WildEcho Studios!**\n\n"
                    "I have turned your idea into an actionable production plan:\n"
                    "1. Suggested channel concept & identity: **WildEcho – Stories from Earth's Quietest Frontiers**\n"
                    "2. Formulated 4-part Season 1 content roadmap\n"
                    "3. Completed Pilot Script Draft ('Secrets of the Urban Wilderness')\n"
                    "4. Activated 5 prioritized tasks across Pre-production, Audio & SEO\n"
                    "5. Documented our consensus to focus on cinematic documentary pacing over talking-head vlogs.\n\n"
                    "What wildlife habitat would you like to explore for Episode 2?"
                ),
                platform="switch"
            )
            db.add(msg1)
            db.add(msg2)

            db.commit()
            logger.info("Demo project seeded successfully!")
    finally:
        db.close()

# Auto-seed if database is fresh
seed_demo_data()


# Event Handler: Links Switch SSE stream directly to AI Agent & Project updates
async def handle_switch_incoming_event(event: dict):
    """Fires when Switch pushes an SSE frame or inbound room message."""
    event_type = event.get("type", "")
    sender_type = event.get("sender_type", "human")
    if (event_type in ("room.message", "message")) and (sender_type in ("human", "user", None)):
        content = event.get("content", "")
        sender = event.get("sender", "Alex")
        logger.info(f"Switch Agent received message from {sender}: {content[:50]}...")
        
        # Process project request via AI agent
        res = await ai_agent.process_project_request(content, sender_name=sender)
        
        # Reply back through Switch Room over official agent protocol
        room_id = event.get("room_id") or switch_client.room_id or settings.SWITCH_ROOM_ID
        await switch_client.post_room_message(
            room_id=room_id,
            content=res["response_text"],
            sender="IdeaFlow Agent",
            thread_id=event.get("thread_id")
        )

        # If live Discord is connected, also mirror reply directly
        if event.get("platform") == "discord" and discord_bridge.is_connected:
            channel_id = event.get("channel_id") or settings.DISCORD_CHANNEL_ID
            if channel_id:
                await discord_bridge.send_discord_reply(
                    channel_id=channel_id,
                    content=res["response_text"],
                    reply_to_id=event.get("discord_message_id")
                )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing IdeaFlow AI backend...")
    init_db()
    seed_demo_data()

    # Configure switch agent event callback
    switch_client.set_event_handler(handle_switch_incoming_event)

    # Start Switch Client (registration, SSE stream, beat loop)
    asyncio.create_task(switch_client.start())

    # Start Discord Bridge (if bot token configured)
    asyncio.create_task(discord_bridge.start())

    yield

    # Shutdown
    logger.info("Shutting down IdeaFlow AI...")
    await switch_client.stop()
    await discord_bridge.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Your Personal Creative Project Manager – Built with Switch Agent Protocol & Discord",
    lifespan=lifespan
)

# Enable CORS for frontend Vite dev server and production builds
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Switch Protocol Hub & API routes
app.include_router(switch_router)
app.include_router(projects.router)
app.include_router(switch_routes.router)
app.include_router(discord_routes.router)
app.include_router(ai_routes.router)

@app.get("/api/health")
def health_check():
    is_connected = switch_client.is_connected
    if not switch_client.is_builtin_hub and switch_client.last_beat_time:
        beat_age = (datetime.now(timezone.utc) - switch_client.last_beat_time).total_seconds()
        if beat_age < 15.0 and switch_client.generation is not None:
            is_connected = True
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "switch_bridge": "connected" if is_connected else "active",
        "switch_agent_id": switch_client.agent_id,
        "discord_status": discord_bridge.status_message,
        "demo_mode": settings.DEMO_MODE
    }

# Mount static frontend production build if present
import os
from fastapi.staticfiles import StaticFiles

dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")

