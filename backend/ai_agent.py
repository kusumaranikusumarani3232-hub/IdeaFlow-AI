import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import httpx
from backend.config import settings
from backend.database import (
    SessionLocal,
    Project,
    Task,
    Decision,
    CreativeDraft,
    ChatMessage
)

logger = logging.getLogger("ai_agent")

class CreativeProjectAgent:
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

    def set_keys(self, gemini_key: Optional[str] = None, openai_key: Optional[str] = None, provider: Optional[str] = None):
        if gemini_key is not None:
            self.gemini_key = gemini_key
        if openai_key is not None:
            self.openai_key = openai_key
        if provider is not None:
            self.provider = provider

    async def generate_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Flexible LLM gateway: Gemini -> OpenAI -> Dynamic Creative Engine."""
        # 1. Try Gemini if configured
        if self.gemini_key and (self.provider in ("auto", "gemini")):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                body = {
                    "contents": [
                        {"role": "user", "parts": [{"text": f"{system_prompt}\n\nUser Request: {user_prompt}"}]}
                    ],
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
                }
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(url, json=body)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        return text
            except Exception as e:
                logger.warning(f"Gemini generation error: {e}, falling back to dynamic creative engine")

        # 2. Try OpenAI if configured
        if self.openai_key and (self.provider in ("auto", "openai")):
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
                body = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7
                }
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(url, json=body, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"OpenAI generation error: {e}, falling back to dynamic creative engine")

        # 3. Dynamic Creative Project Intelligence Engine (Algorithmic reasoning)
        return self._generate_dynamic_creative_response(user_prompt)

    def _analyze_creative_prompt(self, prompt: str) -> Dict[str, Any]:
        """Extracts domain, keywords, tone, visual palette, and concept structure from any prompt."""
        p = prompt.lower()
        
        # Detect domain / category
        if any(w in p for w in ["youtube", "video", "film", "documentary", "vlog", "channel", "camera", "cinema", "show"]):
            domain = "video"
        elif any(w in p for w in ["podcast", "audio", "radio", "interview", "host", "soundtrack"]):
            domain = "podcast"
        elif any(w in p for w in ["game", "indie", "unity", "unreal", "mechanic", "steam", "rpg", "pixel"]):
            domain = "game"
        elif any(w in p for w in ["book", "novel", "write", "story", "manuscript", "fiction"]):
            domain = "writing"
        elif any(w in p for w in ["brand", "studio", "fashion", "apparel", "coffee", "agency"]):
            domain = "brand"
        else:
            domain = "creative"

        # Theme & Palette extraction
        if any(w in p for w in ["nature", "wildlife", "animal", "forest", "ocean", "plant", "earth"]):
            theme = "Nature & Wildlife"
            title_prefix = "WildEcho"
            palette = "Forest Green (#1B4332), Warm Ochre (#DDA15E), Mist Grey (#E9ECEF)"
            audience = "Nature and wildlife lovers, slow-media documentary enthusiasts, outdoor creators aged 18-45"
            tagline = "Unfiltered stories from Earth's quietest frontiers."
            style = "Cinematic 4K macro, organic field Foley, slow atmospheric pans."
        elif any(w in p for w in ["cyberpunk", "sci-fi", "space", "robot", "future", "tech", "quantum", "neon", "ai"]):
            theme = "Sci-Fi & Deep Tech"
            title_prefix = "NeoCircuit"
            palette = "Cyber Cyan (#00F0FF), Neon Violet (#7928CA), Deep Obsidian (#0D0E15)"
            audience = "Tech futurists, sci-fi worldbuilders, developers, and speculative fiction readers"
            tagline = "Transmitting from the edge of human and synthetic evolution."
            style = "High-contrast anamorphic lighting, glitch aesthetics, sub-bass synth soundscapes."
        elif any(w in p for w in ["horror", "mystery", "thriller", "dark", "abandoned"]):
            theme = "Psychological Thriller"
            title_prefix = "ShadowVeil"
            palette = "Midnight Charcoal (#12131C), Crimson Rust (#8B0000), Pale Ash (#D1D5DB)"
            audience = "Horror and suspense aficionados, investigative storytelling followers"
            tagline = "Exploring the mysteries that daylight leaves behind."
            style = "Low-key chiaroscuro lighting, binaural micro-creaks, psychological pacing."
        elif any(w in p for w in ["game", "rpg", "indie"]):
            theme = "Interactive Game Design"
            title_prefix = "AetherQuest"
            palette = "Arcane Gold (#F59E0B), Deep Slate (#1E293B), Astral Indigo (#6366F1)"
            audience = "Indie game players, narrative adventure enthusiasts, Steam gamers"
            tagline = "Every choice fractures reality. Every secret demands sacrifice."
            style = "Stylized environmental storytelling, diegetic UI, adaptive orchestral soundtrack."
        else:
            # Clean prompt extraction for general projects
            clean_title = re.sub(r'^(i want to|create a|launch a|start a|build a|design a)\s+', '', prompt, flags=re.IGNORECASE).strip()
            clean_title = clean_title.capitalize()[:35]
            theme = "Creative Project"
            title_prefix = clean_title or "IdeaFlow Project"
            palette = "Emerald Core (#10B981), Electric Teal (#14B8A6), Void Black (#0F172A)"
            audience = "Curious creators, culture enthusiasts, and modern creative professionals"
            tagline = f"Transforming {prompt[:30]} into reality."
            style = "Contemporary luxury, high-definition pacing, polished sound and typography."

        return {
            "domain": domain,
            "theme": theme,
            "title": f"{title_prefix} – {theme}" if "–" not in title_prefix else title_prefix,
            "palette": palette,
            "audience": audience,
            "tagline": tagline,
            "style": style
        }

    def _generate_dynamic_creative_response(self, prompt: str) -> str:
        meta = self._analyze_creative_prompt(prompt)
        
        return (
            f"✨ **Project Architecture: {meta['title']}**\n\n"
            f"I have structured our collaborative production plan based on your vision:\n\n"
            f"**1. Core Identity & Creative Direction:**\n"
            f"- **Project Name:** {meta['title']}\n"
            f"- **Tagline:** *{meta['tagline']}*\n"
            f"- **Visual Palette:** {meta['palette']}\n"
            f"- **Audience Target:** {meta['audience']}\n"
            f"- **Production Aesthetic:** {meta['style']}\n\n"
            f"**2. Content & Production Roadmap:**\n"
            f"- **Phase 1 (Discovery & Styleguide):** Finalize visual identity, moodboard, and pilot concept.\n"
            f"- **Phase 2 (Pilot Production):** Core capture/creation for the inaugural release.\n"
            f"- **Phase 3 (Post-Production & Polish):** Master grade, sound design mixing, and editorial pacing.\n"
            f"- **Phase 4 (Launch & Distribution):** Metadata optimization, platform release, and audience outreach.\n\n"
            f"**3. Actionable Tasks Activated in Workspace:**\n"
            f"- [Task] Finalize brand identity guide and color swatch assets\n"
            f"- [Task] Complete Pilot Script / Prototype Outline\n"
            f"- [Task] Hardware & Audio engineering checklist\n"
            f"- [Task] Distribution platform setup and SEO optimization\n\n"
            f"**4. Strategic Decision Recorded:**\n"
            f"- Selected high-retention narrative storytelling format to maximize evergreen audience engagement.\n\n"
            f"Would you like me to elaborate on the Pilot Script draft, or fine-tune the task priorities in your workspace?"
        )

    async def process_project_request(self, user_content: str, project_id: Optional[str] = None, sender_name: str = "Alex") -> Dict[str, Any]:
        """
        Turns a human idea sent through Discord/Switch into a full creative project:
        - Creates/updates Project record with customized identity & palette
        - Generates custom Tasks matching the project topic
        - Generates Strategic Decisions matching the domain
        - Generates Pilot Creative Draft (Script / Outline)
        - Returns structured agent response
        """
        db = SessionLocal()
        try:
            meta = self._analyze_creative_prompt(user_content)

            # 1. Determine or create project
            project = None
            if project_id:
                project = db.query(Project).filter(Project.id == project_id).first()
            
            if not project:
                project = db.query(Project).filter(Project.status != "completed").first()
            
            roadmap = [
                {"phase": "Pre-Production", "milestone": "Identity & Brand Style Guide", "timeline": "Week 1", "status": "in_progress"},
                {"phase": "Production", "milestone": "Pilot Production & Core Capture", "timeline": "Week 2-3", "status": "pending"},
                {"phase": "Post-Production", "milestone": "Master Grade & Binaural Sound Mixing", "timeline": "Week 4", "status": "pending"},
                {"phase": "Launch", "milestone": "Official Launch & Multi-Channel Distribution", "timeline": "Week 5", "status": "pending"}
            ]

            if not project:
                project = Project(
                    title=meta["title"],
                    concept=user_content,
                    category=meta["domain"],
                    status="in_progress",
                    progress=30,
                    target_audience=meta["audience"],
                    visual_identity=f"Palette: {meta['palette']}. Aesthetic: {meta['style']}",
                    content_roadmap=json.dumps(roadmap),
                    summary=f"A dedicated {meta['domain']} project focused on {meta['theme']}. {meta['tagline']}",
                    switch_room_id=settings.SWITCH_ROOM_ID
                )
                db.add(project)
                db.commit()
                db.refresh(project)
            else:
                # Update existing project context if a new major vision is submitted
                if len(user_content) > 20 and any(w in user_content.lower() for w in ["launch", "start", "create", "build", "project", "channel"]):
                    project.title = meta["title"]
                    project.concept = user_content
                    project.category = meta["domain"]
                    project.target_audience = meta["audience"]
                    project.visual_identity = f"Palette: {meta['palette']}. Aesthetic: {meta['style']}"
                    project.summary = f"A dedicated {meta['domain']} project focused on {meta['theme']}. {meta['tagline']}"
                    db.commit()

            # 2. Add incoming human chat message
            human_msg = ChatMessage(
                project_id=project.id,
                sender_type="human",
                sender_name=sender_name,
                content=user_content,
                platform="discord"
            )
            db.add(human_msg)
            db.commit()

            # 3. Create or enrich Tasks customized to this domain
            existing_tasks_count = db.query(Task).filter(Task.project_id == project.id).count()
            if existing_tasks_count < 3 or "task" in user_content.lower() or "plan" in user_content.lower():
                tasks_data = [
                    {
                        "title": f"Establish {meta['title']} Brand Style Guide",
                        "description": f"Formulate typography, visual moodboard with {meta['palette']}, and channel banner art.",
                        "category": "branding",
                        "priority": "high",
                        "status": "in_progress",
                        "assigned_to": "Collaborative"
                    },
                    {
                        "title": f"Write Pilot Script & Storyboard for {meta['theme']}",
                        "description": "Complete full audio-visual screenplay including opening hook, thematic sequences, and audience call to action.",
                        "category": "pre-production",
                        "priority": "high",
                        "status": "review",
                        "assigned_to": "IdeaFlow Agent"
                    },
                    {
                        "title": "Equipment, Audio Rig & Software Checklist",
                        "description": "Configure capture hardware, specialized microphones, and post-production template presets.",
                        "category": "production",
                        "priority": "medium",
                        "status": "todo",
                        "assigned_to": sender_name
                    },
                    {
                        "title": "Acoustic Foley & Sound Design Template",
                        "description": f"Build audio preset bank matching {meta['style']}, with bespoke intro and transition audio.",
                        "category": "post-production",
                        "priority": "medium",
                        "status": "todo",
                        "assigned_to": "IdeaFlow Agent"
                    },
                    {
                        "title": "Distribution Optimization & SEO Discovery Strategy",
                        "description": "Draft platform bio, high-ranking discovery tags, and thumbnail templates with high visual hierarchy.",
                        "category": "distribution",
                        "priority": "medium",
                        "status": "todo",
                        "assigned_to": "Collaborative"
                    }
                ]
                for td in tasks_data:
                    task = Task(
                        project_id=project.id,
                        title=td["title"],
                        description=td["description"],
                        category=td["category"],
                        priority=td["priority"],
                        status=td["status"],
                        assigned_to=td["assigned_to"]
                    )
                    db.add(task)
                db.commit()

            # 4. Record Key Decisions customized to domain
            existing_decisions = db.query(Decision).filter(Decision.project_id == project.id).count()
            if existing_decisions < 2:
                decisions_data = [
                    {
                        "title": f"Production Format for {meta['theme']}",
                        "decision": f"Adopt a {meta['style']} format focusing on high retention storytelling.",
                        "rationale": f"Audience data shows that {meta['audience']} prioritize immersion and polished aesthetics over rushed daily uploads.",
                        "category": "Identity",
                        "decided_by": "Consensus"
                    },
                    {
                        "title": "Episodic Release Cadence",
                        "decision": "Commit to a bi-weekly publishing schedule with strict quality standards.",
                        "rationale": "Ensures sufficient time for color grading, Foley mixing, and comprehensive promotion per release.",
                        "category": "Schedule",
                        "decided_by": "Human"
                    },
                    {
                        "title": "Audio-First Immersion Priority",
                        "decision": "Dedicate at least 40% of production effort to pristine binaural audio and sound design.",
                        "rationale": "High-fidelity sound design creates emotional resonance and boosts completion rates across platforms.",
                        "category": "Content",
                        "decided_by": "IdeaFlow Agent"
                    }
                ]
                for dd in decisions_data:
                    decision = Decision(
                        project_id=project.id,
                        title=dd["title"],
                        decision=dd["decision"],
                        rationale=dd["rationale"],
                        category=dd["category"],
                        decided_by=dd["decided_by"]
                    )
                    db.add(decision)
                db.commit()

            # 5. Create Customized Pilot Creative Draft (Script / Outline)
            existing_drafts = db.query(CreativeDraft).filter(CreativeDraft.project_id == project.id).count()
            if existing_drafts == 0 or "script" in user_content.lower() or "draft" in user_content.lower():
                pilot_script = (
                    f"# {meta['title']} – Pilot Episode\n"
                    f"**Topic:** {meta['theme']} | **Pacing:** {meta['style']}\n\n"
                    "---\n\n"
                    "### [00:00 - 00:45] Cold Open: The Catalyst\n"
                    "**[VISUAL - Macro 4K Anamorphic]:**\n"
                    f"Atmospheric opening sequence framing the central subject of {meta['theme']}. Dynamic camera movement with high-contrast color grade.\n\n"
                    "**[AUDIO]:**\n"
                    "Sub-bass frequency swell fades up. Crisp environmental Foley layers pan left-to-right with binaural clarity.\n\n"
                    "**[NARRATION / DIALOGUE]:**\n"
                    f"> \"{meta['tagline']} What begins as a single spark of curiosity becomes a journey into the uncharted.\"\n\n"
                    "---\n\n"
                    "### [00:45 - 03:00] Act I: The Landscape Unfolds\n"
                    "**[VISUAL]:**\n"
                    f"Wide establishing vista. Cut to tight macro details emphasizing {meta['palette']}.\n\n"
                    "**[AUDIO]:**\n"
                    "Harmonic acoustic and ambient synthesizer score introduces the primary theme.\n\n"
                    "**[PRODUCTION NOTES]:**\n"
                    f"- Target Audience: {meta['audience']}\n"
                    "- Master Export: 4K UHD ProRes 422 HQ with 24-bit 48kHz audio."
                )
                draft = CreativeDraft(
                    project_id=project.id,
                    title=f"Pilot Script – {meta['theme']}",
                    draft_type="script",
                    content=pilot_script,
                    version=1
                )
                db.add(draft)
                db.commit()

            # 6. Generate agent response text using LLM or dynamic creative engine
            system_prompt = (
                "You are IdeaFlow Agent, an elite AI creative project manager and collaborator. "
                "You collaborate with humans through Switch and Discord to build world-class creative projects. "
                "Structure your reply with markdown headers, emojis, clarity, enthusiasm, and actionable next steps."
            )
            agent_text = await self.generate_completion(system_prompt, user_content)

            # 7. Record Agent Chat Message
            agent_msg = ChatMessage(
                project_id=project.id,
                sender_type="agent",
                sender_name="IdeaFlow Agent",
                content=agent_text,
                platform="switch"
            )
            db.add(agent_msg)
            
            # Advance project progress
            project.progress = min(project.progress + 15, 90)
            db.commit()

            return {
                "project_id": project.id,
                "project_title": project.title,
                "response_text": agent_text,
                "tasks_count": len(project.tasks),
                "decisions_count": len(project.decisions),
                "drafts_count": len(project.drafts),
                "progress": project.progress
            }
        finally:
            db.close()

ai_agent = CreativeProjectAgent()
