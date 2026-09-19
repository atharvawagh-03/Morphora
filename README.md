# Morphora

[![CI & Tests](https://github.com/atharvawagh-03/Morphora/actions/workflows/ci.yml/badge.svg)](https://github.com/atharvawagh-03/Morphora/actions/workflows/ci.yml)
[![Deploy Showcase](https://github.com/atharvawagh-03/Morphora/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/atharvawagh-03/Morphora/actions/workflows/deploy-pages.yml)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-blue.svg)](https://python.org)
[![TouchDesigner](https://img.shields.io/badge/TouchDesigner-099%20%7C%202023-black.svg)](https://derivative.ca)

Gesture-controlled real-time 3D point cloud morphing — webcam hand gestures morph floating particles between a blue butterfly, red dragon, and dark pink lilies inside a glowing wireframe cube.

**Stack:** Python · MediaPipe · OpenCV · OSC · TouchDesigner · GLSL

---

## 🌐 Showcase Website & Live Demo

Morphora includes a responsive web showcase featuring particle visuals, state diagrams, gesture references, and installation blueprints.

- **Local Preview:**
  ```bash
  python tools/serve_website.py
  # Open http://localhost:8080
  ```
- **Deployment:** Pre-configured for automatic **GitHub Pages**, **Vercel**, and **Netlify** deployments. See [Deployment Guide](docs/DEPLOYMENT.md).

---

## Architecture

```
Python (gesture truth)  ──OSC UDP :7000──▶  TouchDesigner (visual truth)
```

- **Python** captures webcam, detects fist / open palm / pinch, runs a timed state machine, sends OSC.
- **TouchDesigner** receives OSC, drives morph timers, renders 10k-point particle clouds with GLSL shaders.

---

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

### 3. One-Click Gallery / Kiosk Launcher (Windows)
```bash
tools\launch_morphora.bat
```
Automatically initiates the TouchDesigner project and Python gesture engine concurrently.

---

## Gestures

| Gesture | Action |
|---------|--------|
| Left fist → open | Butterfly → Dragon → Lily |
| Right pinch (on Lily) | Toggle cube open |
| Both hands open | Reset to Butterfly |

Press `q` to quit, `r` to force reset.

---

## Test without TouchDesigner

```bash
# Terminal 1 — gesture sender
python main.py

# Terminal 2 — OSC monitor
python test_osc_monitor.py

# State machine unit checks
python test_state_machine.py

# OSC demo sequence (no webcam — for TouchDesigner testing)
python simulate_gestures.py
python simulate_gestures.py --step   # pause between gestures
```

### 3D Models

Ten-thousand-point OBJ placeholders live in `touchdesigner/models/`. Use them while building the TD network, then swap in real `.glb` files later.

Regenerate:
```bash
python tools/generate_point_clouds.py
```

---

## Project structure

```
Morphora/
├── .github/workflows/        # CI/CD: Automated Tests & GitHub Pages Deployment
│   ├── ci.yml                # Python unit tests & model integrity
│   └── deploy-pages.yml      # Automatic GitHub Pages publish
├── python/                   # Gesture detection + OSC sender
│   ├── main.py               # Webcam pipeline
│   ├── config.py             # System constants & states
│   ├── hand_tracker.py       # MediaPipe Tasks wrapper
│   ├── gesture_detector.py   # Geometric classifier
│   ├── state_machine.py      # Timed finite state machine
│   ├── osc_sender.py         # OSC dispatcher
│   ├── simulate_gestures.py  # Mock gesture simulator
│   └── test_*.py             # Unit tests & monitors
├── touchdesigner/            # TD project, models, shaders, scripts
│   ├── main.toe              # Primary TouchDesigner project
│   ├── SETUP.md              # TD build guide
│   ├── models/               # 10,000-point OBJ models
│   ├── shaders/              # GLSL morphing shaders
│   └── scripts/              # Setup & OSC handler scripts
├── website/                  # Showcase landing page (HTML/CSS/JS/WebGL)
│   ├── index.html            # Main showcase structure
│   ├── style.css             # Glassmorphic dark styling
│   ├── script.js             # Interactive particle canvas & UI
│   └── assets/images/        # High-resolution visual captures & favicon
├── tools/                    # Generators & utilities
│   ├── launch_morphora.bat   # Unattended gallery auto-launcher
│   ├── serve_website.py      # Zero-dependency local website previewer
│   └── generate_point_clouds.py # Mathematical OBJ point cloud generator
├── docs/                     # Documentation & guides
│   ├── DEPLOYMENT.md         # Deployment: Web (Pages/Vercel) & Physical (Kiosk)
│   ├── TESTING.md            # Verification procedures
│   └── TROUBLESHOOTING.md    # Common pitfalls & debugging
├── vercel.json               # Zero-config Vercel deployment
└── netlify.toml              # Zero-config Netlify deployment
```

---

## Docs & Guides

- [Deployment Guide (Web & Physical Kiosk)](docs/DEPLOYMENT.md)
- [TouchDesigner setup](touchdesigner/SETUP.md)
- [Testing procedure](docs/TESTING.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

---

## License

See individual 3D model credits in `assets/references/MODEL_CREDITS.md`.
