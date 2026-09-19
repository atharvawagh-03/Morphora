# Morphora Deployment Guide

This document outlines the complete deployment process for **Morphora**, covering both **Online Web Showcase Deployment** and **Physical Exhibition / Museum Kiosk Deployment**.

---

## 1. Online Web Showcase Deployment

The Morphora showcase website (`/website`) presents the project architecture, gesture controls, 3D particle forms, and live documentation.

### Option A: GitHub Pages (Automated CI/CD — Recommended)
This repository includes a pre-configured GitHub Actions workflow: [`.github/workflows/deploy-pages.yml`](../.github/workflows/deploy-pages.yml).

1. Push your repository to GitHub:
   ```bash
   git push origin main
   ```
2. Navigate to your GitHub repository: **Settings** → **Pages**.
3. Under **Build and deployment** → **Source**, select **GitHub Actions**.
4. Any push to `main` touching `website/**` will automatically build and publish the live site at:
   ```
   https://<your-username>.github.io/Morphora/
   ```

### Option B: Vercel (1-Click Deployment)
This repository contains a pre-configured [`vercel.json`](../vercel.json).
1. Import the repository into your [Vercel Dashboard](https://vercel.com).
2. The output directory is automatically routed to `website`.
3. Click **Deploy**. Instant worldwide CDN deployment with zero manual configuration.

### Option C: Netlify
This repository contains [`netlify.toml`](../netlify.toml) with security headers pre-set.
1. Connect repository in [Netlify](https://netlify.com).
2. Publish directory is automatically detected as `website`.
3. Click **Deploy Site**.

### Option D: Local Preview Server
To preview the website locally with no external dependencies:
```bash
python tools/serve_website.py
# Or on custom port:
python tools/serve_website.py --port 8080
```

---

## 2. Interactive Physical Installation Deployment (Gallery / Museum)

Morphora is architected as a two-node system:

```
[Webcam / Sensor Rig]
         │
         ▼
[Python Gesture Tracker] ─── UDP OSC (:7000) ───▶ [TouchDesigner Visual Node]
                                                            │
                                                            ▼
                                                [Projector / 4K LED Screen]
```

### Hardware Specifications

| Component | Minimum Spec | Recommended Spec |
|-----------|--------------|-------------------|
| **GPU** | NVIDIA GTX 1660 / Apple M1 | NVIDIA RTX 3070 / RTX 4070+ |
| **CPU** | Intel Core i5 (10th Gen) / AMD Ryzen 5 | Intel Core i7 (12th Gen+) / Ryzen 7 |
| **Camera** | 720p 30fps USB Webcam | 1080p 60fps wide-angle (Logitech Brio / Elgato Facecam) |
| **Display** | 1080p 60Hz Display | 4K Ultra-short-throw laser projector or large LED wall |
| **Environment** | Even ambient lighting, neutral backdrop | 300–500 lux diffuse lighting, no direct backlighting |

### Setup Steps for Kiosk Deployment

1. **Camera Placement**:
   - Mount the camera at eye-to-chest level (approx. 1.2m – 1.4m height).
   - Position participant standing 1.5m to 2.5m away from the camera.
   - Ensure the field of view covers natural arm reach.

2. **TouchDesigner Configuration**:
   - Launch `touchdesigner/main.toe`.
   - In TouchDesigner Window Placement:
     - Set Window Operator to `/project1/window1` (or perform fullscreen).
     - Target Monitor: Display 2 (Projector/LED).
     - Open in **Perform Mode** (`F1`).

3. **Python Gesture Engine**:
   - Activate environment and launch tracker:
     ```bash
     cd python
     venv\Scripts\activate
     python main.py
     ```
   - Press `h` to toggle the debug HUD if you want a clean view for the operator.

4. **One-Click Startup Script**:
   - Use [`tools/launch_morphora.bat`](../tools/launch_morphora.bat) to start both TouchDesigner and Python simultaneously.
   - To configure automated startup on machine boot (Windows):
     - Press `Win + R`, type `shell:startup`, press Enter.
     - Create a shortcut to `tools/launch_morphora.bat` in that folder.

---

## 3. Remote / Distributed Network Deployment

If running the Python tracker on an edge device (e.g. Raspberry Pi 5, Intel NUC, or mini PC) separate from the TouchDesigner visual rendering workstation:

1. Connect both machines to the same high-speed gigabit switch or local Wi-Fi.
2. Edit [`python/config.py`](../python/config.py):
   ```python
   # Replace "127.0.0.1" with the IP address of the TouchDesigner machine
   OSC_IP = "192.168.1.100"
   OSC_PORT = 7000
   ```
3. In TouchDesigner:
   - Ensure firewall allows UDP inbound on port `7000`.
   - Verify heartbeat signals via the `/morphora/alive` OSC channel.

---

## 4. Verification & Diagnostic Commands

Validate health before opening to the public:

```bash
# 1. Verify state machine transitions
cd python
python test_state_machine.py

# 2. Run automated OSC demo without a camera
python simulate_gestures.py

# 3. Monitor live OSC traffic
python test_osc_monitor.py
```
