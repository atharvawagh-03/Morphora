# Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Fist never detected | Threshold too strict | Lower `FIST_DISTANCE_THRESHOLD` in `config.py` |
| Open palm triggers constantly | Threshold too low | Raise `OPEN_PALM_DISTANCE_THRESHOLD` |
| Pinch fires twice | No hysteresis gap | Widen gap between `PINCH_CLOSE_THRESHOLD` / `PINCH_OPEN_THRESHOLD` |
| TD never receives OSC | Port mismatch | Confirm `OSC_PORT` == OSC In CHOP port (7000) |
| Morph snaps instantly | Timer mismatch | Keep TD `timer_morph` at 2.5s = `MORPH_DURATION_SEC` |
| Morph looks like noise | Point count mismatch | Re-scatter all models to exactly 10,000 points, same seed |
| Left/right swapped | Double mirror | Python flips frame; do NOT flip TD Video Device In |
| Low FPS | Bloom / debug window | Lower Bloom quality; set `SHOW_DEBUG_WINDOW = False` |
