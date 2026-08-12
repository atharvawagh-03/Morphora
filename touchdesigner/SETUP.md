# TouchDesigner Setup Guide

Build `main.toe` following these steps. Timer lengths **must match** `python/config.py` (`MORPH_DURATION_SEC = 2.5`).

## 7.1 OSC Receiver

1. **OSC In CHOP** — Network Port `7000`, blank address pattern
2. **Select CHOP** — pull `/gesture/state` channel
3. **Logic CHOP** — detect state value changes → trigger pulses
4. **CHOP Execute DAT** (recommended for string events):

```python
# Listen on /gesture/event
def onValueChange(channel, sampleIndex, val, prev):
    addr = channel.owner.path
    return

def onOffToOn(channel, sampleIndex, val, prev):
    return

# Wire via OSC In → DAT callback or use a Text DAT with:
# if args[0] == 'left_fist_open': op('trig_morph_dragon').par.triggerpulse.pulse()
```

Trigger CHOPs: `trig_morph_dragon`, `trig_morph_lily`, `trig_cube`

## 7.2 Timers

| CHOP | Length | Drives |
|------|--------|--------|
| `timer_morph` | 2.5s | `uMorphT` (fraction export) |
| `timer_explode` | 0.4s | `uExplodeAmt` (inverted: `1 - fraction`) |
| `timer_cube` | 0.6s | cube scale / glow on CUBE_OPEN |

## 7.3 SOP Network (×3 models)

Per model (`butterfly`, `dragon`, `lily`):

```
File SOP → Facet SOP (Unique Points) → Scatter SOP (10000, fixed seed)
→ Attribute Create SOP (Cd colors) → Null SOP
```

**Colors (Section 11):**
- Butterfly wings: `#00C2FF`, body: `#0A0A0C`
- Dragon: `#FF1E2D` / `#5C0A0A`
- Lily: `#C2185B` center, `#FFF8F0` edges

## 7.4 Merge + targetP

1. **Switch SOP** driven by `/gesture/state` picks current cloud
2. Copy target cloud `P` → point attribute `targetP` on current cloud (1:1 index match)
3. Output **Null SOP** `morph_ready`

## 7.5 Geometry + GLSL MAT

1. **Geometry COMP** — SOP = `morph_ready`, Render as Points ON
2. **GLSL MAT** — paste `shaders/particle_morph.vert` / `.frag`
3. Add vertex attribute `targetP` (vec3)
4. Uniforms: `uMorphT`, `uTime`, `uExplodeAmt`, `uSwirlStrength`, `uNoiseAmp`, `uPointSize`

Suggested defaults:
- `uSwirlStrength` = 0.4
- `uNoiseAmp` = 0.25
- `uPointSize` = 3.0

## 7.6–7.8 Render + Composite

```
Video Device In TOP (webcam, NO flip)
Render TOP (particles + cube + camera + lights)
Composite TOP (webcam under particles)
→ Bloom TOP (threshold 0.6–0.7) → Level TOP → Null TOP
```

**Cube:** Box SOP, Render as Lines, white `#FFFFFF` @ 40% alpha. Animate scale/glow from `timer_cube`.

## Models

Place `.glb` files in this folder:
- `butterfly.glb`
- `dragon.glb`
- `lily.glb`

See `assets/references/MODEL_CREDITS.md` for sourcing.
