"""Timed state machine — Python owns gesture truth."""

from __future__ import annotations

import time

from config import MORPH_DURATION_SEC, STATE_NAMES, SystemState


class StateMachine:
    def __init__(self) -> None:
        self.state = SystemState.BUTTERFLY
        self._morph_start: float | None = None

    @property
    def is_mid_morph(self) -> bool:
        return self.state in (SystemState.MORPH_TO_DRAGON, SystemState.MORPH_TO_LILY)

    @property
    def is_settled(self) -> bool:
        return not self.is_mid_morph

    def tick(self) -> bool:
        """Auto-advance morph states after MORPH_DURATION_SEC. Returns True on change."""
        if not self.is_mid_morph or self._morph_start is None:
            return False

        if time.monotonic() - self._morph_start >= MORPH_DURATION_SEC:
            if self.state == SystemState.MORPH_TO_DRAGON:
                self._enter(SystemState.DRAGON)
            elif self.state == SystemState.MORPH_TO_LILY:
                self._enter(SystemState.LILY)
            return True
        return False

    def handle_event(self, event: str) -> bool:
        """Process a confirmed gesture edge. Returns True if state changed."""
        if event == "left_fist_open":
            if self.state == SystemState.BUTTERFLY:
                self._enter(SystemState.MORPH_TO_DRAGON)
                return True
            if self.state == SystemState.DRAGON:
                self._enter(SystemState.MORPH_TO_LILY)
                return True

        elif event == "right_pinch":
            if self.state == SystemState.LILY:
                self._enter(SystemState.CUBE_OPEN)
                return True
            if self.state == SystemState.CUBE_OPEN:
                self._enter(SystemState.LILY)
                return True

        elif event == "two_hand_open":
            if self.is_settled and self.state != SystemState.BUTTERFLY:
                self._enter(SystemState.BUTTERFLY)
                return True

        return False

    def force_reset(self) -> None:
        self._enter(SystemState.BUTTERFLY)

    def _enter(self, state: SystemState) -> None:
        self.state = state
        if self.is_mid_morph:
            self._morph_start = time.monotonic()
        else:
            self._morph_start = None

    def state_label(self) -> str:
        return STATE_NAMES.get(self.state, str(self.state))
