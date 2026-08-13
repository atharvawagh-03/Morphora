"""
Send a scripted gesture sequence over OSC — test TouchDesigner without a webcam.

Usage:
    cd python
    python simulate_gestures.py          # auto demo (full cycle)
    python simulate_gestures.py --step    # press Enter between steps
"""

from __future__ import annotations

import argparse
import sys
import time

from config import MORPH_DURATION_SEC, SystemState
from osc_sender import OSCSender


def _pause(step_mode: bool, msg: str) -> None:
    print(msg)
    if step_mode:
        input("  [Enter] next step...")


def run_demo(step_mode: bool = False) -> None:
    osc = OSCSender()
    d = MORPH_DURATION_SEC + 0.3

    def hands(left: str, right: str) -> None:
        osc.send_hands(left, right)
        osc.send_alive()

    def go(state: SystemState, left: str = "neutral", right: str = "neutral") -> None:
        osc.send_state(state)
        hands(left, right)
        print(f"  state -> {state.name}")

    _pause(step_mode, ">> Start: BUTTERFLY")
    go(SystemState.BUTTERFLY, "open", "none")

    _pause(step_mode, ">> left_fist_open -> MORPH_TO_DRAGON")
    osc.send_event("left_fist_open")
    go(SystemState.MORPH_TO_DRAGON, "open", "none")
    time.sleep(d)
    go(SystemState.DRAGON, "open", "none")

    _pause(step_mode, ">> left_fist_open -> MORPH_TO_LILY")
    osc.send_event("left_fist_open")
    go(SystemState.MORPH_TO_LILY, "open", "none")
    time.sleep(d)
    go(SystemState.LILY, "open", "none")

    _pause(step_mode, ">> right_pinch -> CUBE_OPEN")
    osc.send_event("right_pinch")
    go(SystemState.CUBE_OPEN, "open", "pinch")
    time.sleep(1.0)

    _pause(step_mode, ">> right_pinch -> LILY")
    osc.send_event("right_pinch")
    go(SystemState.LILY, "open", "open")
    time.sleep(0.8)

    _pause(step_mode, ">> two_hand_open -> BUTTERFLY reset")
    osc.send_event("two_hand_open")
    go(SystemState.BUTTERFLY, "open", "open")

    print("\nDemo complete.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Morphora OSC gesture simulator")
    parser.add_argument("--step", action="store_true", help="Wait for Enter between steps")
    args = parser.parse_args()

    print("Morphora OSC simulator -> 127.0.0.1:7000")
    print("Start TouchDesigner OSC In before running.\n")

    try:
        run_demo(step_mode=args.step)
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
