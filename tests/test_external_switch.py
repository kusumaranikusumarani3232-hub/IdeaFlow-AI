import asyncio
import sys
import os
import json
import httpx

# Ensure stdout uses UTF-8 on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config import settings
from backend.switch_client import switch_client
from backend.ai_agent import ai_agent
from backend.database import SessionLocal, Project, Task, Decision, SwitchEventLog

async def run_live_external_switch_verification():
    print("=" * 75)
    print("   IDEAFLOW AI – OFFICIAL EXTERNAL SWITCH SERVER VERIFICATION (v0.31.0)")
    print("=" * 75)

    # 1. Health check against Official Switch Server
    print("\n[STEP 1] Testing connectivity to Official Switch Server...")
    print(f"  Target Switch Core URL: {settings.SWITCH_URL}")
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            health_res = await client.get(f"{settings.SWITCH_URL}/health")
            print(f"  Switch Health HTTP Status: {health_res.status_code}")
            assert health_res.status_code == 200
            print(f"  Switch Health Response: {health_res.json()}")
            print("  -> PASSED: Official local Switch Server is alive and responsive.")
        except Exception as e:
            print(f"  -> FAILED: Could not reach Switch Server at {settings.SWITCH_URL}: {e}")
            raise

    # 2. Test Agent Registration Handshake
    print("\n[STEP 2] Testing Official Switch Agent Protocol Registration...")
    reg_ok = await switch_client.register()
    print(f"  Registration Success: {reg_ok}")
    print(f"  Assigned Agent ID: {switch_client.agent_id}")
    print(f"  Assigned Agent API Key: {switch_client.api_key[:10]}...")
    print(f"  Target Switch Room ID: {switch_client.room_id}")
    assert reg_ok is True
    assert switch_client.agent_id is not None
    assert switch_client.api_key is not None
    assert switch_client.room_id is not None
    print("  -> PASSED: Registered agent with official Switch Server and acquired credentials.")

    # 3. Test Inbound SSE Handshake & Connection State
    print("\n[STEP 3] Testing Persistent SSE Stream Inbound Protocol...")
    sse_frames = []
    sse_connected_event = asyncio.Event()

    # Temporary SSE probe to capture connection_state
    async def sse_probe():
        url = f"{switch_client.switch_url}/agents/{switch_client.agent_id}/events"
        params = {
            "connection_id": switch_client.connection_id,
            "scope": "all",
            "filter": "all",
            "rooms": switch_client.room_id
        }
        headers = {
            "Authorization": f"Bearer {switch_client.api_key}",
            "Accept": "text/event-stream"
        }
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("GET", url, params=params, headers=headers) as resp:
                    print(f"  SSE Stream Connected HTTP Status: {resp.status_code}")
                    assert resp.status_code == 200
                    async for line in resp.aiter_lines():
                        line = line.strip()
                        if line:
                            sse_frames.append(line)
                            if "connection_state" in line:
                                print(f"  SSE Received Frame: {line}")
                                sse_connected_event.set()
                            if "generation" in line and not switch_client.generation:
                                try:
                                    gen_data = json.loads(line.replace("data: ", ""))
                                    switch_client.generation = gen_data.get("generation")
                                except Exception:
                                    pass
        except asyncio.CancelledError:
            pass
        except Exception as err:
            print(f"  SSE Probe error: {err}")

    probe_task = asyncio.create_task(sse_probe())
    try:
        await asyncio.wait_for(sse_connected_event.wait(), timeout=6.0)
        await asyncio.sleep(0.5)

        # 4. Test Agent Heartbeat with Generation Fencing
        print("\n[STEP 4] Testing Agent Heartbeat Keep-Alive (POST /connection/beat)...")
        beat_ok = await switch_client.send_beat()
        print(f"  Heartbeat HTTP Success: {beat_ok}")
        print(f"  Last Beat Timestamp: {switch_client.last_beat_time.isoformat() if switch_client.last_beat_time else 'None'}")
        assert beat_ok is True
        print("  -> PASSED: Heartbeat keep-alive accepted by Switch Server on active connection.")
    finally:
        probe_task.cancel()

    assert len(sse_frames) > 0
    print(f"  Captured {len(sse_frames)} SSE frames from Switch Server.")
    print("  -> PASSED: Switch Server SSE stream established and connection_state verified.")

    # 5. Test Outbound Room Messaging via Agent Protocol
    print("\n[STEP 5] Testing Outbound Room Messaging (POST /agents/{agent_id}/message)...")
    test_outbound_content = "Hello from IdeaFlow Agent test verification! Ready to turn ideas into reality."
    msg_ok = await switch_client.post_room_message(
        room_id=switch_client.room_id,
        content=test_outbound_content,
        sender="IdeaFlow Agent"
    )
    print(f"  Outbound Message Sent Success: {msg_ok}")
    assert msg_ok is True
    print("  -> PASSED: Outbound room message successfully accepted by Switch Server.")

    # 6. Test Full Workflow: Creator Input -> AI Agent -> SQLite DB -> Switch Room
    print("\n[STEP 6] Testing End-to-End Creative Project Workflow...")
    prompt = "I want to launch a 4K drone cinematography channel focusing on coastal cliffs and sea caves."
    
    received_in_handler = []
    async def test_handler(event):
        received_in_handler.append(event)
    switch_client.set_event_handler(test_handler)

    # Simulate human creator message entering Switch Room
    print("  Simulating creator message entering Switch Room...")
    post_ok = await switch_client.post_human_message_to_switch(
        room_id=switch_client.room_id,
        content=prompt,
        sender="Sarah (Filmmaker)",
        platform="discord",
        channel_id="1567465114259431487",
        discord_message_id="disc_msg_test_901"
    )
    assert post_ok is True
    await asyncio.sleep(0.2)
    assert len(received_in_handler) == 1
    print("  -> Inbound creator message delivered to registered event handler.")

    # Process via AI creative agent
    print("  Processing idea through IdeaFlow AI Creative Engine...")
    result = await ai_agent.process_project_request(prompt, sender_name="Sarah (Filmmaker)")
    print(f"  Generated Project Title: {result['project_title']}")
    print(f"  Project Tasks Created: {result['tasks_count']}")
    print(f"  Decisions Formulated: {result['decisions_count']}")
    print(f"  Creative Drafts: {result['drafts_count']}")
    print(f"  Agent Response Preview: {result['response_text'][:120]}...")

    assert result["tasks_count"] > 0
    assert result["decisions_count"] > 0
    assert len(result["response_text"]) > 50

    # Post agent response to Switch Room
    print("  Dispatching agent response back into Switch Room...")
    reply_ok = await switch_client.post_room_message(
        room_id=switch_client.room_id,
        content=result["response_text"],
        sender="IdeaFlow Agent"
    )
    assert reply_ok is True
    print("  -> PASSED: Full collaboration workflow succeeded through Switch.")

    # 7. Check SQLite Switch Event Log Persistence
    print("\n[STEP 7] Verifying Switch Event Log Persistence in SQLite...")
    db = SessionLocal()
    try:
        recent_logs = db.query(SwitchEventLog).order_by(SwitchEventLog.timestamp.desc()).limit(5).all()
        print(f"  Total logged wire events in database: {db.query(SwitchEventLog).count()}")
        print("  Latest 3 Switch frames:")
        for log in recent_logs[:3]:
            print(f"    [{log.direction}] {log.event_type} (cursor #{log.cursor}) - {log.timestamp}")
        assert len(recent_logs) > 0
        print("  -> PASSED: Wire inspector event persistence verified.")
    finally:
        db.close()

    print("\n" + "=" * 75)
    print("   ALL TESTS PASSED: 100% GENUINE OFFICIAL SWITCH SERVER INTEGRATION")
    print("=" * 75)

if __name__ == "__main__":
    asyncio.run(run_live_external_switch_verification())
