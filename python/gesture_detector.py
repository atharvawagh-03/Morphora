"""Geometric gesture detection with stability buffer and edge-trigger cooldown."""

from __future__ import annotations

import math
import time
from collections import deque

from config import (
    EVENT_COOLDOWN_SEC,
    FIST_DISTANCE_THRESHOLD,
    OPEN_PALM_DISTANCE_THRESHOLD,
    PINCH_CLOSE_THRESHOLD,
    PINCH_OPEN_THRESHOLD,
    STABILITY_FRAMES,
)
from hand_tracker import HandLandmarks

# MediaPipe landmark indices
WRIST = 0
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_MCP = 9
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20

FINGERTIPS = (INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP)

HandPose = str  # none | fist | open | pinch | neutral


def _dist(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def _palm_center(landmarks: HandLandmarks) -> tuple[float, float, float]:
    wrist = landmarks[WRIST]
    middle_mcp = landmarks[MIDDLE_MCP]
    return (
        (wrist[0] + middle_mcp[0]) / 2,
        (wrist[1] + middle_mcp[1]) / 2,
        (wrist[2] + middle_mcp[2]) / 2,
    )


def _scale(landmarks: HandLandmarks) -> float:
    return max(_dist(landmarks[WRIST], landmarks[MIDDLE_MCP]), 1e-6)


def is_fist(landmarks: HandLandmarks) -> bool:
    center = _palm_center(landmarks)
    scale = _scale(landmarks)
    distances = [_dist(landmarks[t], center) / scale for t in FINGERTIPS]
    return max(distances) < FIST_DISTANCE_THRESHOLD


def is_open_palm(landmarks: HandLandmarks) -> bool:
    center = _palm_center(landmarks)
    scale = _scale(landmarks)
    distances = [_dist(landmarks[t], center) / scale for t in FINGERTIPS]
    return min(distances) > OPEN_PALM_DISTANCE_THRESHOLD


class GestureDetector:
    def __init__(self) -> None:
        self._left_buffer: deque[HandPose] = deque(maxlen=STABILITY_FRAMES)
        self._right_buffer: deque[HandPose] = deque(maxlen=STABILITY_FRAMES)
        self._left_stable: HandPose = "none"
        self._right_stable: HandPose = "none"
        self._left_prev: HandPose = "none"
        self._right_prev: HandPose = "none"
        self._left_pinch_active = False
        self._right_pinch_active = False
        self._last_event_time = 0.0

    def _pinch_pose(self, landmarks: HandLandmarks, active: bool) -> tuple[HandPose, bool]:
        thumb = landmarks[THUMB_TIP]
        index = landmarks[INDEX_TIP]
        pinch_dist = _dist(thumb, index) / _scale(landmarks)

        if active:
            if pinch_dist > PINCH_OPEN_THRESHOLD:
                return "open", False
            return "pinch", True
        if pinch_dist < PINCH_CLOSE_THRESHOLD:
            return "pinch", True
        return "neutral", False

    def _classify(self, landmarks: HandLandmarks | None, side: str) -> HandPose:
        if landmarks is None:
            if side == "left":
                self._left_pinch_active = False
            else:
                self._right_pinch_active = False
            return "none"

        active = self._left_pinch_active if side == "left" else self._right_pinch_active
        pinch_pose, pinch_active = self._pinch_pose(landmarks, active)
        if side == "left":
            self._left_pinch_active = pinch_active
        else:
            self._right_pinch_active = pinch_active

        if pinch_pose == "pinch":
            return "pinch"

        if is_fist(landmarks):
            return "fist"
        if is_open_palm(landmarks):
            return "open"
        return "neutral"

    @staticmethod
    def _stable_pose(buffer: deque[HandPose]) -> HandPose:
        if len(buffer) < STABILITY_FRAMES:
            return "none"
        first = buffer[0]
        if all(p == first for p in buffer):
            return first
        return "none"

    def update(self, hands: dict[str, HandLandmarks | None]) -> tuple[HandPose, HandPose, list[str]]:
        raw_left = self._classify(hands.get("Left"), "left")
        raw_right = self._classify(hands.get("Right"), "right")

        self._left_buffer.append(raw_left)
        self._right_buffer.append(raw_right)

        left = self._stable_pose(self._left_buffer) if hands.get("Left") else "none"
        right = self._stable_pose(self._right_buffer) if hands.get("Right") else "none"

        if left == "none" and hands.get("Left"):
            left = raw_left if raw_left != "neutral" else "neutral"
        if right == "none" and hands.get("Right"):
            right = raw_right if raw_right != "neutral" else "neutral"

        events: list[str] = []
        now = time.monotonic()

        if now - self._last_event_time >= EVENT_COOLDOWN_SEC:
            if self._left_prev == "fist" and left == "open":
                events.append("left_fist_open")
            if self._right_prev == "pinch" and right not in ("pinch", "none"):
                events.append("right_pinch")
            if (
                left == "open"
                and right == "open"
                and (self._left_prev != "open" or self._right_prev != "open")
            ):
                events.append("two_hand_open")

            if events:
                self._last_event_time = now

        self._left_prev = left if left != "none" else self._left_prev
        self._right_prev = right if right != "none" else self._right_prev
        self._left_stable = left
        self._right_stable = right

        return left, right, events

    @property
    def left_pose(self) -> HandPose:
        return self._left_stable

    @property
    def right_pose(self) -> HandPose:
        return self._right_stable
