"""Quick state machine transition tests — no pytest required."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from state_machine import StateMachine
from config import SystemState


def assert_state(sm: StateMachine, expected: SystemState, msg: str) -> None:
    assert sm.state == expected, f"{msg}: expected {expected.name}, got {sm.state.name}"


def run_tests() -> None:
    sm = StateMachine()
    assert_state(sm, SystemState.BUTTERFLY, "initial")

    sm.handle_event("left_fist_open")
    assert_state(sm, SystemState.MORPH_TO_DRAGON, "butterfly to dragon morph")

    sm.state = SystemState.DRAGON
    sm.handle_event("left_fist_open")
    assert_state(sm, SystemState.MORPH_TO_LILY, "dragon to lily morph")

    sm.state = SystemState.LILY
    sm.handle_event("right_pinch")
    assert_state(sm, SystemState.CUBE_OPEN, "lily to cube")

    sm.handle_event("right_pinch")
    assert_state(sm, SystemState.LILY, "cube back to lily")

    sm.state = SystemState.DRAGON
    changed = sm.handle_event("two_hand_open")
    assert changed and sm.state == SystemState.BUTTERFLY, "two-hand reset from dragon"

    sm.state = SystemState.MORPH_TO_DRAGON
    changed = sm.handle_event("two_hand_open")
    assert not changed, "two-hand ignored during morph"

    sm.force_reset()
    assert_state(sm, SystemState.BUTTERFLY, "manual reset")

    print("All state machine tests passed.")


if __name__ == "__main__":
    run_tests()
