# Testing Procedure

## 1. Python isolated test

```bash
cd python
venv\Scripts\activate
python main.py
```

Confirm debug overlay:
- STATE updates on gestures
- LEFT / RIGHT labels track hands
- FPS stable (>20)

## 2. OSC sanity check

Use an OSC monitor on port **7000**. Expect every frame:

```
/gesture/left   "open"|"fist"|"pinch"|"neutral"|"none"
/gesture/right  ...
/gesture/alive  1
```

On state change: `/gesture/state` (0–5)  
On gesture edge: `/gesture/event` string

## 3. TouchDesigner CHOP verification

OSC In CHOP → spreadsheet view. Trigger gestures, confirm channels update.

## 4. Morph-only test

Bypass timers — drive `uMorphT` with a slider 0→1. Confirm coherent shape morph.

## 5. End-to-end

Run Python + TD together:

| # | Gesture | Expected state |
|---|---------|----------------|
| 1 | Left fist → open | BUTTERFLY → DRAGON |
| 2 | Left fist → open | DRAGON → LILY |
| 3 | Right pinch | LILY → CUBE_OPEN |
| 4 | Right pinch | CUBE_OPEN → LILY |
| 5 | Both hands open | → BUTTERFLY |

Test with 2–3 people; tune thresholds in `config.py` if needed.
