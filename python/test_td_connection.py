"""
Diagnostic script — tests OSC connection to TouchDesigner.

Usage:
    cd python
    python test_td_connection.py

Opens TouchDesigner with OSC In on port 7000 FIRST, then run this.
Sends a sequence of known states and events, printing each one so you
can verify that TD's osc_in CHOP shows them arriving.
"""

from __future__ import annotations

import sys
import time

from config import OSC_PORT, SystemState
from osc_sender import OSCSender


def main() -> int:
    osc = OSCSender()

    print("=" * 50)
    print("  Morphora OSC Connection Diagnostic")
    print(f"  Sending to 127.0.0.1:{OSC_PORT}")
    print("=" * 50)
    print()

    # ── Test 1: Alive heartbeat ──────────────────────────────────────────
    print("[1/5] Sending /gesture/alive = 1 ...")
    for _ in range(5):
        osc.send_alive()
        time.sleep(0.1)
    print("  ✓ Check osc_in CHOP: /gesture/alive channel should show 1")
    print()

    # ── Test 2: State integer ────────────────────────────────────────────
    print("[2/5] Sending /gesture/state = 0 (BUTTERFLY) ...")
    osc.send_state(SystemState.BUTTERFLY)
    time.sleep(0.5)
    # Force resend by clearing cache
    osc._last_state = None
    osc.send_state(SystemState.BUTTERFLY)
    print("  ✓ Check select_state CHOP: should show 0")
    print("  ✓ Particles should be CYAN butterfly shape")
    print()

    input("  Press Enter to send DRAGON state...")
    print("[3/5] Sending /gesture/state = 2 (DRAGON) ...")
    osc._last_state = None
    osc.send_state(SystemState.DRAGON)
    time.sleep(0.5)
    print("  ✓ Check select_state CHOP: should show 2")
    print("  ✓ After ~2.5s lag, particles should morph to RED dragon")
    print()

    input("  Press Enter to send LILY state...")
    print("[4/5] Sending /gesture/state = 4 (LILY) ...")
    osc._last_state = None
    osc.send_state(SystemState.LILY)
    time.sleep(0.5)
    print("  ✓ Check select_state CHOP: should show 4")
    print("  ✓ After ~2.5s lag, particles should morph to PINK lily")
    print()

    input("  Press Enter to test events...")
    print("[5/5] Sending /gesture/event = 'left_fist_open' ...")
    osc.send_event("left_fist_open")
    time.sleep(0.3)
    print("  ✓ Check select_event CHOP: should show string value")
    print()

    # ── Reset ────────────────────────────────────────────────────────────
    print("Resetting to BUTTERFLY...")
    osc._last_state = None
    osc.send_state(SystemState.BUTTERFLY)
    osc.send_event("two_hand_open")
    time.sleep(0.5)

    print()
    print("=" * 50)
    print("  Diagnostic complete!")
    print()
    print("  If you see channels updating in TD's osc_in CHOP,")
    print("  the connection is working correctly.")
    print()
    print("  If nothing appears:")
    print("  1. Confirm osc_in CHOP port = 7000")
    print("  2. Check Windows Firewall isn't blocking UDP")
    print("  3. Re-run build_network.py in Textport")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
