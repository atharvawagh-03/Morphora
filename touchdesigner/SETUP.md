# TouchDesigner Setup Guide

Build `main.toe` in TouchDesigner 2023+. Timer lengths **must match** `python/config.py` (`MORPH_DURATION_SEC = 2.5`).

## Fastest path — auto-build script (~5 min)

1. Open TouchDesigner → **File → New**
2. **Dialogs → Textport and DAT Editor**
3. Set your repo path (if not `D:/Morphora`):
   ```python
   import os
   os.environ['MORPHORA_ROOT'] = r'D:/Morphora'
   ```
4. Run the builder:
   ```python
   exec(open(r'D:/Morphora/touchdesigner/scripts/build_network.py').read())
   ```
5. **File → Save** as `touchdesigner/main.toe`
6. In a terminal, run the OSC simulator:
   ```powershell
   cd D:\Morphora\python
   python simulate_gestures.py
   ```
   Or run `python main.py` with your webcam.

The script creates `/project1/morphora` with OSC In, timers, model SOPs, GLSL MAT, render/composite/bloom, and a Window COMP.

### After auto-build — manual tweaks

- [ ] Confirm **OSC In** port = **7000** and channels appear when Python runs
- [ ] Pulse `trig_morph_dragon` manually — particles should morph
- [ ] Wire **Video Device In** to your webcam (no horizontal flip)
- [ ] On **mat_particles**, confirm `uMorphT` / `uExplodeAmt` exports if not auto-wired
- [ ] Add **geo_cube** to **render1** geometry list if cube doesn't show

---

## Quick checklist

- [ ] OSC In CHOP on port **7000**
- [ ] Three model SOP chains → `butterfly_out`, `dragon_out`, `lily_out`
- [ ] Merge network → `morph_ready` with `targetP` attribute
- [ ] GLSL MAT with shaders from `shaders/`
- [ ] Render + Composite + Bloom pipeline
- [ ] Wireframe cube with CUBE_OPEN animation

---

## Step 1 — New project

1. File → New
2. Save as `touchdesigner/main.toe`

---

## Step 2 — OSC receiver (`/project1/osc_in`)

| Operator | Parameter | Value |
|----------|-----------|-------|
| **OSC In CHOP** `osc_in` | Network Port | `7000` |
| | Address Pattern | *(blank — receive all)* |
| | Active | ON |

Add operators:

| Operator | Purpose |
|----------|---------|
| **Select CHOP** `select_state` | Channel `/gesture/state` |
| **Select CHOP** `select_event` | Channel `/gesture/event` |
| **Select CHOP** `select_left` | Channel `/gesture/left` |
| **Select CHOP** `select_right` | Channel `/gesture/right` |

**CHOP Execute DAT** `event_handler`:
- Copy script from `scripts/osc_event_handler.py`
- Connect `select_event` as input

**Trigger CHOPs** (one pulse each):
- `trig_morph_dragon`
- `trig_morph_lily`
- `trig_cube`

---

## Step 3 — Timers

| CHOP | Length (s) | Trigger | Export |
|------|------------|---------|--------|
| `timer_morph` | **2.5** | `trig_morph_*` | `fraction` → GLSL `uMorphT` |
| `timer_explode` | **0.4** | same pulse as morph | `1 - fraction` → `uExplodeAmt` |
| `timer_cube` | **0.6** | `trig_cube` | cube scale / glow |

**Math CHOP** on explode timer:
```
1 - me.inputVal
```
Clamp 0–1.

---

## Step 4 — Model SOP networks (use placeholder OBJs first)

Placeholder files (10,000 verts each) are in `models/`:
- `butterfly_10k.obj`
- `dragon_10k.obj`
- `lily_10k.obj`

Per model, build this chain:

```
File SOP → Facet SOP → Null SOP
```

| Operator | Settings |
|----------|----------|
| **File SOP** | Load `.obj` or `.glb` |
| **Facet SOP** | Unique Points = ON |
| **Scatter SOP** | Only if vertex count ≠ 10000 — Force Total Count = **10000**, Seed = **42** |
| **Attribute Create SOP** | Add `Cd` (see colors below) |
| **Null SOP** | Name: `butterfly_out` / `dragon_out` / `lily_out` |

### Colors (PRD Section 11)

| Model | Cd assignment |
|-------|---------------|
| Butterfly | Wings `#00C2FF`, body `#0A0A0C` |
| Dragon | `#FF1E2D` highlights, `#5C0A0A` body |
| Lily | Center `#C2185B`, edges `#FFF8F0` |

Use **Point SOP** or **Attribute Create** with distance-from-center rules for petal gradient on lily.

---

## Step 5 — Morph merge (`targetP`)

Goal: current cloud points carry a `targetP` attribute for the GLSL shader.

1. **Switch SOP** `switch_current` — picks active shape from state:
   - Input 0: `butterfly_out`
   - Input 1: `dragon_out`
   - Input 2: `lily_out`
   - Index: expression from `select_state` (map states 0,2,4 to inputs)

2. **Switch SOP** `switch_target` — picks morph destination:
   - During MORPH_TO_DRAGON (state 1): target = `dragon_out`
   - During MORPH_TO_LILY (state 3): target = `lily_out`
   - Otherwise: target = same as current

3. **Attribute Copy SOP** or **Point SOP**:
   - Copy `P` from target switch → attribute `targetP` on current cloud
   - **Critical:** all clouds must have exactly **10,000 points** in matching order

4. **Null SOP** `morph_ready` — output to Geometry COMP

---

## Step 6 — GLSL particle material

1. **Geometry COMP** `geo_particles`
   - SOP: `morph_ready`
   - Render → Points = ON
   - Point Size: driven by uniform

2. **GLSL MAT** `mat_particles`
   - Vertex Shader: paste `shaders/particle_morph.vert`
   - Pixel Shader: paste `shaders/particle_morph.frag`
   - **Vectors page** — add uniforms:

| Uniform | Type | Source |
|---------|------|--------|
| `uMorphT` | float | Export CHOP `timer_morph/fraction` |
| `uTime` | float | `absTime.seconds` |
| `uExplodeAmt` | float | Math CHOP after explode timer |
| `uSwirlStrength` | float | `0.4` |
| `uNoiseAmp` | float | `0.25` |
| `uPointSize` | float | `3.0` |

3. **Vertex Attributes page** — bind `targetP` (vec3) from SOP

4. Assign `mat_particles` to `geo_particles`

See `scripts/morph_uniforms.md` for expression reference.

---

## Step 7 — Camera, lights, cube

**Camera COMP** `cam1`:
- Translate: `(0, 0, 4)`, look at origin

**Light COMP** `key`:
- Soft key from upper-left

**Light COMP** `rim`:
- Low intensity rim from behind (ember/cyan read)

**Wireframe cube** `geo_cube`:
```
Box SOP → Material (white, 40% alpha, Render as Lines)
```
- Scale ~1.2
- On CUBE_OPEN: export `timer_cube/fraction` to scale (1.0 → 1.15) and material glow

---

## Step 8 — Compositing TOPs

```
videodevin1 (webcam, NO horizontal flip)
    ↓
composite1 (Over) ← render1 (particles + cube)
    ↓
bloom1 (Threshold 0.6–0.7)
    ↓
level1 (exposure/gamma trim)
    ↓
null_out (final output → Window COMP / projector)
```

**Important:** Python mirrors the webcam. Do **not** flip Video Device In TOP or hands will be swapped.

---

## Step 9 — Test order

1. **Python only** — `python main.py`, confirm debug overlay
2. **OSC monitor** — `python test_osc_monitor.py` in second terminal
3. **TD OSC** — spreadsheet view on `osc_in`
4. **Morph scrub** — slider on `uMorphT` 0→1 before wiring timers
5. **End-to-end** — both running, all 5 gestures

Full procedure: `docs/TESTING.md`

---

## Upgrading placeholder models

1. Download CC-licensed `.glb` from Sketchfab (see `assets/references/MODEL_CREDITS.md`)
2. Replace File SOP paths
3. Re-scatter to exactly **10,000** points, seed **42**
4. Re-author `Cd` colors
5. Commit: `feat: replace placeholder OBJ models with GLB assets`

---

## Performance tips

- Cache scattered result as `.bgeo` File SOP once happy with distribution
- Lower Bloom quality before reducing particle count
- Set Common → FPS target to 60, monitor with Alt+Y

See `docs/TROUBLESHOOTING.md`.
