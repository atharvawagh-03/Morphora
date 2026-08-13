# 3D Model Credits

## Placeholder models (included)

Procedural 10,000-point OBJ placeholders ship in `touchdesigner/models/`:

| File | Description |
|------|-------------|
| `butterfly_10k.obj` | Wing ellipsoids + body (dev/testing) |
| `dragon_10k.obj` | Serpentine spine + wings |
| `lily_10k.obj` | Radial petals + center |

Regenerate anytime:
```bash
python tools/generate_point_clouds.py
```

## Production models (replace placeholders)

Download CC-licensed `.glb` files and export to `touchdesigner/`:

| Model | Suggested sources | Target file |
|-------|-------------------|-------------|
| Butterfly | [Sketchfab](https://sketchfab.com) — Free + Downloadable | `butterfly.glb` |
| Dragon | [Sketchfab](https://sketchfab.com) | `dragon.glb` |
| Lily | [Sketchfab](https://sketchfab.com) | `lily.glb` |

After importing in TouchDesigner:
1. Facet → Unique Points
2. Scatter → **10000** points, seed **42**
3. Re-author `Cd` colors per PRD Section 11

**TODO:** Add attribution lines here once final models are chosen.
