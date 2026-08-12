"""Shared configuration — single source of truth for Python and TD sync."""

from enum import IntEnum

# ── OSC ──────────────────────────────────────────────────────────────────────
OSC_IP = "127.0.0.1"
OSC_PORT = 7000

OSC_ADDR_STATE = "/gesture/state"
OSC_ADDR_EVENT = "/gesture/event"
OSC_ADDR_LEFT = "/gesture/left"
OSC_ADDR_RIGHT = "/gesture/right"
OSC_ADDR_ALIVE = "/gesture/alive"

# ── Camera ───────────────────────────────────────────────────────────────────
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
CAMERA_INDEX = 0
FLIP_FRAME = True  # mirror for natural interaction; keep TD Video Device In un-flipped

# ── MediaPipe ────────────────────────────────────────────────────────────────
MODEL_COMPLEXITY = 1          # 0 = faster, 1 = more accurate
MIN_DETECTION_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.5
MAX_NUM_HANDS = 2

# ── Gesture thresholds (normalized by wrist→middle-MCP length) ───────────────
FIST_DISTANCE_THRESHOLD = 0.35
OPEN_PALM_DISTANCE_THRESHOLD = 0.55
PINCH_CLOSE_THRESHOLD = 0.045
PINCH_OPEN_THRESHOLD = 0.065

# ── Debouncing ───────────────────────────────────────────────────────────────
STABILITY_FRAMES = 4
EVENT_COOLDOWN_SEC = 0.6

# ── State machine timing (must match TD timer_morph length) ──────────────────
MORPH_DURATION_SEC = 2.5

# ── Debug ────────────────────────────────────────────────────────────────────
SHOW_DEBUG_WINDOW = True
DEBUG_WINDOW_NAME = "Morphora — Gesture Debug"


class SystemState(IntEnum):
    BUTTERFLY = 0
    MORPH_TO_DRAGON = 1
    DRAGON = 2
    MORPH_TO_LILY = 3
    LILY = 4
    CUBE_OPEN = 5


STATE_NAMES = {
    SystemState.BUTTERFLY: "BUTTERFLY",
    SystemState.MORPH_TO_DRAGON: "MORPH→DRAGON",
    SystemState.DRAGON: "DRAGON",
    SystemState.MORPH_TO_LILY: "MORPH→LILY",
    SystemState.LILY: "LILY",
    SystemState.CUBE_OPEN: "CUBE_OPEN",
}
