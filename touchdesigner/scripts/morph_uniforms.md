# Morph Uniform Expressions (TouchDesigner)

Copy these into GLSL MAT uniform parameters or Math CHOP expressions.

## uMorphT
Export directly from `timer_morph` channel `fraction`.

## uExplodeAmt
Math CHOP after `timer_explode/fraction`:
```
1 - me.inputVal
```
Clamp output 0–1.

## uTime
GLSL MAT uniform expression:
```
absTime.seconds
```

## uSwirlStrength
Default: `0.4`

## uNoiseAmp
Default: `0.25`

## uPointSize
Default: `3.0` — increase for projector installs.

## Current shape index (Switch SOP)
Based on `/gesture/state` integer:

| State | Value | Visible shape |
|-------|-------|---------------|
| BUTTERFLY | 0 | butterfly |
| MORPH_TO_DRAGON | 1 | butterfly → dragon |
| DRAGON | 2 | dragon |
| MORPH_TO_LILY | 3 | dragon → lily |
| LILY | 4 | lily |
| CUBE_OPEN | 5 | lily (cube animates) |

## targetP merge expression (Point SOP / Attribute Create)

When morphing 0→1 or 2→3, set `targetP` from the destination Null SOP:
- State 1: copy `dragon_out` P → targetP
- State 3: copy `lily_out` P → targetP

Use an Attribute Copy SOP or Script SOP — see SETUP.md section 7.4.
