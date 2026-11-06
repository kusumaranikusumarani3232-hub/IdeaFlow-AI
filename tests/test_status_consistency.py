import sys
import os
import httpx
from datetime import datetime, timezone

# Ensure stdout uses UTF-8 on Windows
sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://127.0.0.1:8000"

def map_frontend_status(switch_status):
    """Exact JavaScript mapping logic from frontend/src/components/Navbar.jsx and SwitchInspector.jsx"""
    if not switch_status:
        return {"badge": "Connecting...", "is_online": False}
    
    is_switch_online = bool(switch_status.get("is_connected"))
    is_builtin = bool(switch_status.get("is_builtin"))
    
    if is_builtin:
        badge = "Built-in Hub"
    elif is_switch_online:
        badge = "Official Switch (Live)"
    else:
        badge = "External (Offline)"
        
    return {
        "badge": badge,
        "is_online": is_switch_online,
        "is_builtin": is_builtin
    }

def test_status_mapping_and_api():
    print("=" * 75)
    print("   IDEAFLOW AI – STATUS CONSISTENCY & MAPPING TEST")
    print("=" * 75)

    # 1. Unit Test Frontend Mapping Logic
    print("\n[STEP 1] Testing Frontend Status Mapping Unit Cases...")
    
    # Case A: Live External Switch
    case_live = {"is_connected": True, "is_builtin": False, "generation": 8589934659}
    res_live = map_frontend_status(case_live)
    print(f"  Live External Case Result: {res_live}")
    assert res_live["badge"] == "Official Switch (Live)"
    assert res_live["is_online"] is True

    # Case B: Offline External Switch
    case_offline = {"is_connected": False, "is_builtin": False, "generation": None}
    res_offline = map_frontend_status(case_offline)
    print(f"  Offline External Case Result: {res_offline}")
    assert res_offline["badge"] == "External (Offline)"
    assert res_offline["is_online"] is False

    # Case C: Built-in Hub Mode
    case_builtin = {"is_connected": True, "is_builtin": True}
    res_builtin = map_frontend_status(case_builtin)
    print(f"  Built-in Hub Case Result: {res_builtin}")
    assert res_builtin["badge"] == "Built-in Hub"
    print("  -> PASSED: All mapping logic unit cases verified.")

    # 2. Live API Probe against Running Backend
    print("\n[STEP 2] Probing Live Backend API (/api/switch/status)...")
    with httpx.Client(timeout=5.0) as client:
        res = client.get(f"{API_URL}/api/switch/status")
        print(f"  HTTP Status: {res.status_code}")
        assert res.status_code == 200
        data = res.json()
        print(f"  Switch URL: {data.get('switch_url')}")
        print(f"  Mode: {data.get('mode')}")
        print(f"  Is Builtin: {data.get('is_builtin')}")
        print(f"  Agent ID: {data.get('agent_id')}")
        print(f"  Connection ID: {data.get('connection_id')}")
        print(f"  Generation Fence: {data.get('generation')}")
        print(f"  Is Connected: {data.get('is_connected')}")
        print(f"  Last Beat: {data.get('last_beat_time')}")

        assert data.get("is_builtin") is False
        assert data.get("is_connected") is True
        assert data.get("generation") is not None
        assert data.get("connection_id") is not None

        # Apply frontend mapping to actual live API response
        mapped = map_frontend_status(data)
        print(f"\n  Mapped Dashboard Badge: '{mapped['badge']}'")
        assert mapped["badge"] == "Official Switch (Live)"
        assert mapped["is_online"] is True
        print("  -> PASSED: Live API maps strictly to 'Official Switch (Live)'.")

    # 3. Test Heartbeat Keep-Alive Endpoint
    print("\n[STEP 3] Probing Live Manual Beat (/api/switch/beat)...")
    with httpx.Client(timeout=5.0) as client:
        beat_res = client.post(f"{API_URL}/api/switch/beat")
        print(f"  Beat HTTP Status: {beat_res.status_code}")
        assert beat_res.status_code == 200
        beat_data = beat_res.json()
        print(f"  Beat Response: {beat_data}")
        assert beat_data.get("success") is True
        print("  -> PASSED: Heartbeat keep-alive accepted by official Switch Core.")

    # 4. Test Health Check Endpoint
    print("\n[STEP 4] Probing Health Endpoint (/api/health)...")
    with httpx.Client(timeout=5.0) as client:
        health_res = client.get(f"{API_URL}/api/health")
        assert health_res.status_code == 200
        health_data = health_res.json()
        print(f"  Health Response: {health_data}")
        assert health_data.get("switch_bridge") == "connected"
        print("  -> PASSED: Health endpoint confirms switch_bridge is 'connected'.")

    print("\n" + "=" * 75)
    print("   ALL TESTS PASSED: DASHBOARD & SWITCH INSPECTOR CONSISTENCY VERIFIED")
    print("=" * 75)

if __name__ == "__main__":
    test_status_mapping_and_api()

