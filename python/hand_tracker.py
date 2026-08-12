"""MediaPipe hand tracking wrapper with OpenCV webcam capture."""

from __future__ import annotations

import cv2
import mediapipe as mp
import numpy as np

from config import (
    CAMERA_INDEX,
    FLIP_FRAME,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MODEL_COMPLEXITY,
)

HandLandmarks = list[tuple[float, float, float]]  # normalized x, y, z


class HandTracker:
    def __init__(self) -> None:
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            model_complexity=MODEL_COMPLEXITY,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        self._mp_draw = mp.solutions.drawing_utils
        self._cap = cv2.VideoCapture(CAMERA_INDEX)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    def read(self) -> tuple[bool, np.ndarray | None, dict[str, HandLandmarks | None]]:
        ok, frame = self._cap.read()
        if not ok:
            return False, None, {"Left": None, "Right": None}

        if FLIP_FRAME:
            frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)

        hands: dict[str, HandLandmarks | None] = {"Left": None, "Right": None}
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_lm, handedness in zip(
                results.multi_hand_landmarks, results.multi_handedness
            ):
                label = handedness.classification[0].label  # "Left" or "Right"
                landmarks = [(lm.x, lm.y, lm.z) for lm in hand_lm.landmark]
                hands[label] = landmarks

        return True, frame, hands

    def draw(self, frame: np.ndarray, hands: dict[str, HandLandmarks | None]) -> None:
        for label, landmarks in hands.items():
            if landmarks is None:
                continue
            # Rebuild a minimal landmark list for drawing
            hand_landmarks = self._mp_hands.HandLandmark
            # Use MediaPipe drawing on a synthetic structure via direct plot
            h, w = frame.shape[:2]
            for idx, (x, y, _z) in enumerate(landmarks):
                cx, cy = int(x * w), int(y * h)
                cv2.circle(frame, (cx, cy), 3, (0, 255, 180) if label == "Left" else (255, 120, 80), -1)
            # Label near wrist
            wx, wy = int(landmarks[0][0] * w), int(landmarks[0][1] * h)
            cv2.putText(frame, label, (wx, wy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def release(self) -> None:
        self._hands.close()
        self._cap.release()

    @staticmethod
    def landmark(landmarks: HandLandmarks, index: int) -> tuple[float, float, float]:
        return landmarks[index]
