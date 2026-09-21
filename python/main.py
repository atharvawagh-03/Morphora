"""Main loop — webcam → gestures → state machine → OSC."""

from __future__ import annotations

import sys
import time

import cv2

from config import DEBUG_WINDOW_NAME, SHOW_DEBUG_WINDOW
from gesture_detector import GestureDetector
from hand_tracker import HandTracker
from osc_sender import OSCSender
from state_machine import StateMachine


def _draw_overlay(frame, state_label: str, left: str, right: str, fps: float) -> None:
    lines = [
        f"STATE: {state_label}",
        f"LEFT:  {left}",
        f"RIGHT: {right}",
        f"FPS:   {fps:.1f}",
        "",
        "Left fist->open: morph",
        "Right pinch: cube toggle",
        "Both open: reset",
        "q=quit  r=reset",
    ]
    y = 30
    for line in lines:
        cv2.putText(frame, line, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (240, 240, 240), 1, cv2.LINE_AA)
        y += 22


def main() -> int:
    tracker = HandTracker()
    detector = GestureDetector()
    state_machine = StateMachine()
    osc = OSCSender()

    prev_time = time.monotonic()
    fps = 0.0

    print("Morphora gesture sender running. OSC -> 127.0.0.1:7000")
    print("Press q in debug window to quit.")

    try:
        while True:
            ok, frame, hands = tracker.read()
            if not ok or frame is None:
                print("Camera read failed.", file=sys.stderr)
                break

            left, right, events = detector.update(hands)

            state_changed = False
            for event in events:
                if state_machine.handle_event(event):
                    state_changed = True
                    osc.send_event(event)
                    print(f"EVENT: {event} → {state_machine.state_label()}")

            if state_machine.tick():
                state_changed = True
                print(f"AUTO: → {state_machine.state_label()}")

            if state_changed:
                osc.send_state(state_machine.state)

            osc.send_hands(left, right)
            osc.send_alive()

            now = time.monotonic()
            dt = now - prev_time
            prev_time = now
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt)

            if SHOW_DEBUG_WINDOW:
                tracker.draw(frame, hands)
                _draw_overlay(frame, state_machine.state_label(), left, right, fps)
                cv2.imshow(DEBUG_WINDOW_NAME, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                if key == ord("r"):
                    state_machine.force_reset()
                    osc.send_state(state_machine.state)
                    osc.send_event("two_hand_open")
                    print("Manual reset → BUTTERFLY")

    except KeyboardInterrupt:
        pass
    finally:
        tracker.release()
        if SHOW_DEBUG_WINDOW:
            cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
