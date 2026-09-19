"""MediaPipe hand tracking wrapper with OpenCV webcam capture."""

from __future__ import annotations

import time
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from config import (
    CAMERA_INDEX,
    FLIP_FRAME,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
)

HandLandmarks = list[tuple[float, float, float]]  # normalized x, y, z

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_PATH = Path(__file__).resolve().parent / "models" / "hand_landmarker.task"


def _ensure_model() -> Path:
    if MODEL_PATH.exists():
        return MODEL_PATH
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading hand landmarker model → {MODEL_PATH}")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    return MODEL_PATH


class HandTracker:
    def __init__(self) -> None:
        options = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(_ensure_model())),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=MAX_NUM_HANDS,
            min_hand_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._start_time = time.monotonic()

        # On Windows, cv2.CAP_DSHOW is much faster and more reliable than MSMF
        cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened() and CAMERA_INDEX == 0:
            cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap = cv2.VideoCapture(1)

        self._cap = cap
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    def _timestamp_ms(self) -> int:
        return int((time.monotonic() - self._start_time) * 1000)

    def read(self) -> tuple[bool, object | None, dict[str, HandLandmarks | None]]:
        ok, frame = self._cap.read()
        if not ok:
            return False, None, {"Left": None, "Right": None}

        if FLIP_FRAME:
            frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = self._landmarker.detect_for_video(mp_image, self._timestamp_ms())

        hands: dict[str, HandLandmarks | None] = {"Left": None, "Right": None}
        if results.hand_landmarks and results.handedness:
            for landmarks, handedness in zip(results.hand_landmarks, results.handedness):
                label = handedness[0].category_name  # "Left" or "Right"
                hands[label] = [(lm.x, lm.y, lm.z) for lm in landmarks]

        return True, frame, hands

    def draw(self, frame, hands: dict[str, HandLandmarks | None]) -> None:
        h, w = frame.shape[:2]
        for label, landmarks in hands.items():
            if landmarks is None:
                continue
            color = (0, 255, 180) if label == "Left" else (255, 120, 80)
            for x, y, _z in landmarks:
                cv2.circle(frame, (int(x * w), int(y * h)), 3, color, -1)
            wx, wy = int(landmarks[0][0] * w), int(landmarks[0][1] * h)
            cv2.putText(
                frame, label, (wx, wy - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2,
            )

    def release(self) -> None:
        self._landmarker.close()
        self._cap.release()

    @staticmethod
    def landmark(landmarks: HandLandmarks, index: int) -> tuple[float, float, float]:
        return landmarks[index]
