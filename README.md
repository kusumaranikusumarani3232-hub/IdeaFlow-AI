# IdeaFlow AI – Your Personal Creative Project Manager
### *Flip the Switch Hackathon 2026 – Track 02: Best Personal or Creative Workflow*

[![Switch Agent Protocol](https://img.shields.io/badge/Switch_Protocol-v1.0_(SSE+HTTP)-00E599?style=flat-square)](https://github.com/sandbox-quantum/switch)
[![Discord Gateway](https://img.shields.io/badge/Discord-Bot_&_Bridge-5865F2?style=flat-square)](https://discord.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.115+-009688?style=flat-square)](https://fastapi.tiangolo.com)
[![React 19 + Vite](https://img.shields.io/badge/Frontend-React_19_+_Vite_8-61DAFB?style=flat-square)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Design-Tailwind_CSS_v4-38B2AC?style=flat-square)](https://tailwindcss.com)

---

## 🌟 Executive Summary

**IdeaFlow AI** transforms scattered creative thoughts into finished, world-class projects through real-time collaboration between human creators and autonomous AI teammates.

Instead of confining agents to isolated terminal prompts or web forms, **IdeaFlow AI integrates the open-source Switch message bus and agent protocol (`sandbox-quantum/switch`) directly into team chat**. A creator simply drops an idea into Discord:

> **Creator in Discord:** *"I want to launch a YouTube channel about nature and wildlife."*

Connected through Switch as an active teammate in the channel room, the **IdeaFlow Agent** autonomously:
1. 🌿 **Understands and structures the idea** into a coherent brand identity (*WildEcho Studios*).
2. 🎯 **Defines target audience & visual aesthetics** (color palettes, cinematography guidelines).
3. 📅 **Builds a 4-Phase content roadmap** (Pre-production, Pilot Filming, 4K Color Grade, Launch).
4. 🎬 **Generates full production drafts** (cinematic pilot script with macro camera notes and binaural Foley cues).
5. 📋 **Breaks work into prioritized tasks** across human and AI assignees.
6. ⚖️ **Tracks strategic consensus decisions** (e.g., narrative-documentary pacing over vlogs).
7. 💬 **Maintains bidirectional collaboration** across Discord and the web studio.

---

## ⚡ The Switch Integration (Judging Priority: 30%)

Switch is the central nervous system of IdeaFlow AI—not a superficial add-on.

IdeaFlow AI strictly implements the official **Switch Agent Protocol** specified in [`sandbox-quantum/switch`](https://github.com/sandbox-quantum/switch):

```
┌─────────────────┐           ┌──────────────────────────────────────┐           ┌────────────────────────┐
│  Human Creator  │           │             SWITCH CORE              │           │     IdeaFlow Agent     │
│  (Discord Chat) │           │     (Open-Source Message Bus)        │           │    (Autonomous Teammate)│
└────────┬────────┘           └──────────────────┬───────────────────┘           └───────────┬────────────┘
         │                                       │                                           │
         │ 1. Mention: "@IdeaFlow Nature idea"   │                                           │
         ├──────────────────────────────────────>│                                           │
         │                                       │ 2. SSE Inbound Stream (GET /agents/events)│
         │                                       ├──────────────────────────────────────────>│
         │                                       │                                           │
         │                                       │                                           │ 3. Understands Idea
         │                                       │                                           │    Generates Tasks
         │                                       │                                           │    Writes Pilot Script
         │                                       │                                           │    Records Decisions
         │                                       │                                           │
         │                                       │ 4. Outbound Room Post (POST /rooms/msgs)  │
         │                                       │<──────────────────────────────────────────┤
         │                                       │                                           │
         │ 5. Relays Agent Response to Channel   │                                           │
         │<──────────────────────────────────────┤                                           │
         │                                       │                                           │
         │                                       │ 6. Heartbeat Loop (POST /connection/beat) │
         │                                       │< - - - - - - - - - - - - - - - - - - - - -┤ (Every 8 seconds)
```

### 1. Agent Registration Handshake
The agent registers out-of-band with the Switch Core using the administrative token:
- **Endpoint:** `POST /agents`
- **Header:** `Authorization: Bearer ${AGENT_REGISTRATION_TOKEN}`
- **Payload:** `{"name": "IdeaFlow Agent", "connection_model": "always_on"}`
- **Response:** Yields unique `agent_id` and secret credential `agent_secret`.

### 2. Inbound Server-Sent Events (SSE) Stream
Maintains a persistent downstream stream for instant event delivery:
- **Endpoint:** `GET /agents/{id}/events?connection_id={uuid}&cursor={cursor}`
- **Headers:** `Authorization: Bearer ${agent_secret}`, `Accept: text/event-stream`
- Receives real-time frames: `event: message`, `event: ping`, `event: task`.

### 3. Heartbeat & Cursor Management
To maintain room slots and avoid stale disconnects:
- **Endpoint:** `POST /agents/{id}/connection/beat`
- **Body:** `{"connection_id": "conn_...", "cursor": 14}`
- Beats every 8 seconds; handles reconnects on 404/409 codes.

### 4. Outbound Room Messaging
When the agent responds to the creator:
- **Endpoint:** `POST /rooms/{room_id}/messages`
- **Body:** `{"content": "...", "sender": "IdeaFlow Agent", "sender_type": "agent", "thread_id": "..."}`

### 5. Dual-Mode Switch Flexibility
- **Mode A (External Switch Server):** Connects to any self-hosted Switch Docker instance (`http://localhost:8000`).
- **Mode B (Built-in Switch Hub Engine):** Embedded Switch protocol hub located at `/switch/api`, allowing developers to test the full Switch architecture out-of-the-box with zero setup hurdles.

---

## 🎨 Application Architecture & Features

### 1. Dashboard Overview
- Real-time project KPIs: Creative Progress %, Task Completion Ratio, Active Projects.
- Live Switch Protocol Telemetry bar (Room ID, Agent Model, Frame Cursor).
- Quick Idea Starters (Nature YouTube, Tech Podcast, Indie Adventure Game).
- Recent Agent Activity timeline.

### 2. Project Workspace
- **Roadmap & Concept:** Visual palette hex cards (`#1B4332`, `#DDA15E`, `#E9ECEF`), Target Audience persona, and 4-Phase milestone timeline.
- **Task Management:** Interactive Kanban cards with categories (Pre-production, Production, Post-production, Branding, Distribution), priorities, and assignee tags (`IdeaFlow Agent`, `Alex (Creator)`, `Collaborative`).
- **Creative Drafts & Materials:** Full-length pilot screenplays with timestamps, macro camera notes, binaural audio cues, copy-to-clipboard, and versioning.
- **Shared Decisions Log:** Transparent record of decisions and rationales agreed upon by human and agent.
- **Collaboration History:** Live chat feed streaming messages between Discord and the Switch room.

### 3. AI Creative Studio
- **Brand Ideator:** Generates channel names, taglines, color palettes, and unique value propositions.
- **Milestone Decomposer:** Converts high-level milestones into granular technical tasks.
- **Cinematic Scriptwriter:** Screenplay generator with audiovisual cue formatting.

### 4. Switch Protocol Inspector (Hackathon Judge Showcase!)
- **Live Wire Log:** Live monitor showing every packet passing through Switch (`INBOUND` SSE frames, `OUTBOUND` message deliveries, `HEARTBEAT` beats).
- **Discord Inbound Simulator:** Interactive panel allowing evaluators to simulate Discord creator messages with 1 click and witness the entire Switch agent reaction loop in real time.
- **Manual Beat Trigger:** Test server response time and cursor updates.

### 5. Project Completion & Deliverables Dossier
- Export complete project brief as **Markdown (`.md`)** or **JSON**.
- Deliverable validation checklist.

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python 3.10+** (Tested on Python 3.13)
- **Node.js 18+** (Tested on Node 24)

### 1. Clone & Setup Backend
```bash
git clone https://github.com/your-username/IdeaFlow-AI.git
cd "IdeaFlow AI"

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` configuration works out of the box with zero external keys required!

```env
# Switch Infrastructure Configuration
SWITCH_URL=http://localhost:8000/switch/api
AGENT_REGISTRATION_TOKEN=switch_ideaflow_token_2026
AGENT_NAME=IdeaFlow Agent
SWITCH_ROOM_ID=room_discord_nature_channel
CONNECTION_MODEL=always_on

# Real Discord Bot (Optional: Leave blank to use built-in simulator)
DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_ID=

# AI Model Configuration (Optional: built-in creative engine used if blank)
GEMINI_API_KEY=
OPENAI_API_KEY=
AI_PROVIDER=auto
```

### 3. Launch IdeaFlow AI (Single Unified Server)
Start the FastAPI server, which hosts the API, the Switch protocol bridge, and the pre-built React dashboard simultaneously:
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser!

### 4. (Optional) Run Frontend in Development Mode
If you want hot-reloading for frontend modifications:
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)**.

---

## 🧪 End-to-End Demonstration Workflow

Follow these steps to evaluate the end-to-end human-agent collaboration flow:

1. **Open the Dashboard:** Navigate to `http://localhost:8000`.
2. **Observe the Switch Status:** Look at the top status bar. The badge indicates `Switch: Protocol Live (always_on)` and `Cursor: #...`.
3. **Trigger the Creative Workflow:**
   - On the Dashboard, click **"Run Hackathon Demo Workflow"** (or open the **Switch Inspector** tab).
   - Send: *"I want to launch a YouTube channel about nature and wildlife."*
4. **Inspect the Switch Protocol Wire:**
   - Click the **Switch Inspector** tab.
   - You will see the **INBOUND** SSE frame arrive, the agent cursor update, and the **OUTBOUND** response dispatched to the Switch room.
5. **Explore the Generated Project:**
   - Click **Project Workspace**:
     - **Roadmap & Identity:** Review the generated channel identity (*WildEcho*), aesthetic color swatches, and 4-phase milestone plan.
     - **Task Management:** View the 5 tasks broken down by the agent (e.g. *"Field Equipment & Audio Setup Checklist"*). Click **Mark Done** on a task to advance project progress.
     - **Creative Drafts:** Read the generated Episode 1 Pilot Script (*"Secrets of the Urban Wilderness"*) complete with macro visual camera directions, audio cues, and voiceover dialogue.
     - **Shared Decisions:** Review the consensus log (e.g. *"Adopt cinematic documentary style over vlog format"*).
6. **Export Deliverables:**
   - Click **Deliverables**.
   - Click **"Download .MD"** to download the complete creative project dossier.

---

## 🤖 Connecting Real Discord (Optional)

To connect a live Discord server to Switch:
1. Visit the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new Application & Bot.
3. Enable **Privileged Gateway Intents** -> **Message Content Intent**.
4. In your `.env` file, set:
   ```env
   DISCORD_BOT_TOKEN=your_bot_token_here
   DISCORD_CHANNEL_ID=your_target_channel_id
   ```
5. Restart IdeaFlow AI. The bot will log in and show `Discord: Connected as @IdeaFlowBot`.
6. Tag `@IdeaFlow` in your channel and watch the agent respond directly in Discord!

---

## 🏆 Hackathon Alignment

| Criteria | Weight | Implementation in IdeaFlow AI |
|---|---|---|
| **Switch Integration** | **30%** | Full native implementation of the Switch Agent Protocol: Registration (`POST /agents`), SSE Inbound streaming (`GET /agents/{id}/events`), Heartbeat cursor loop (`POST /connection/beat`), Outbound room messages (`POST /rooms/{room_id}/messages`), and a dedicated Protocol Wire Inspector. |
| **Technical Execution** | **25%** | Production-ready FastAPI + React 19 + Tailwind v4 architecture with SQLite persistence, async background tasks, graceful error handling, and zero-downtime hot-reloading. |
| **Creativity & Impact** | **25%** | Solves the #1 creative hurdle (turning scattered thoughts into completed deliverables) by acting as an executive producer and collaborator right inside team chat. |
| **Presentation** | **20%** | Luxury dark-mode aesthetic with custom glassmorphism, responsive components, live protocol visualizers, and comprehensive documentation. |

---

*IdeaFlow AI – Built for Flip the Switch Hackathon 2026.*
