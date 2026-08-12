# Morphora

Gesture-controlled real-time 3D point cloud morphing — webcam hand gestures morph floating particles between a blue butterfly, red dragon, and dark pink lilies inside a glowing wireframe cube.

**Stack:** Python · MediaPipe · OpenCV · OSC · TouchDesigner · GLSL

## Architecture

```
Python (gesture truth)  ──OSC UDP :7000──▶  TouchDesigner (visual truth)
```

- **Python** captures webcam, detects fist / open palm / pinch, runs a timed state machine, sends OSC.
- **TouchDesigner** receives OSC, drives morph timers, renders 10k-point particle clouds with GLSL shaders.

## Quick start

### 1. Python

```bash
cd python
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python main.py
```

### 2. TouchDesigner

1. Open `touchdesigner/main.toe` (build following `touchdesigner/SETUP.md`)
2. Set OSC In CHOP Network Port = **7000**
3. Run Python + TD together

### 3. Gestures

| Gesture | Action |
|---------|--------|
| Left fist → open | Butterfly → Dragon → Lily |
| Right pinch (on Lily) | Toggle cube open |
| Both hands open | Reset to Butterfly |

Press `q` to quit, `r` to force reset.

## Project structure

```
Morphora/
├── python/           # Gesture detection + OSC sender
├── touchdesigner/    # TD project, models, shaders
├── assets/           # Textures, screenshots, references
└── docs/             # Testing & troubleshooting
```

## Docs

- [TouchDesigner setup](touchdesigner/SETUP.md)
- [Testing procedure](docs/TESTING.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## License

See individual 3D model credits in `assets/references/MODEL_CREDITS.md`.
