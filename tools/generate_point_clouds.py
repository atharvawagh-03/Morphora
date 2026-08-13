"""
Generate three standardized 10,000-point OBJ clouds for TouchDesigner.

Usage:
    python tools/generate_point_clouds.py

Outputs:
    touchdesigner/models/butterfly_10k.obj
    touchdesigner/models/dragon_10k.obj
    touchdesigner/models/lily_10k.obj

Replace these with real .glb models later — keep point count at 10,000.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

POINT_COUNT = 10_000
SEED = 42
OUT_DIR = Path(__file__).resolve().parents[1] / "touchdesigner" / "models"


def sample_ellipsoid(
    rng: random.Random,
    center: tuple[float, float, float],
    radii: tuple[float, float, float],
    count: int,
) -> list[tuple[float, float, float]]:
    cx, cy, cz = center
    rx, ry, rz = radii
    pts: list[tuple[float, float, float]] = []
    for _ in range(count):
        u = rng.random() * math.tau
        v = rng.random()
        r = math.sqrt(v)
        x = cx + rx * r * math.cos(u)
        y = cy + ry * r * math.sin(u)
        z = cz + rz * (rng.random() - 0.5) * 0.35
        pts.append((x, y, z))
    return pts


def sample_line(
    rng: random.Random,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    count: int,
    jitter: float = 0.03,
) -> list[tuple[float, float, float]]:
    pts: list[tuple[float, float, float]] = []
    for _ in range(count):
        t = rng.random()
        x = start[0] + (end[0] - start[0]) * t + (rng.random() - 0.5) * jitter
        y = start[1] + (end[1] - start[1]) * t + (rng.random() - 0.5) * jitter
        z = start[2] + (end[2] - start[2]) * t + (rng.random() - 0.5) * jitter
        pts.append((x, y, z))
    return pts


def sample_petals(
    rng: random.Random,
    count: int,
    petals: int = 8,
) -> list[tuple[float, float, float]]:
    pts: list[tuple[float, float, float]] = []
    per_petal = count // petals
    for i in range(petals):
        angle = (i / petals) * math.tau
        cx = math.cos(angle) * 0.35
        cy = math.sin(angle) * 0.12
        cz = math.sin(angle * 2) * 0.05
        pts.extend(
            sample_ellipsoid(rng, (cx, cy, cz), (0.28, 0.12, 0.06), per_petal)
        )
    while len(pts) < count:
        pts.append((0.0, 0.0, rng.uniform(-0.08, 0.08)))
    return pts[:count]


def build_butterfly(rng: random.Random) -> list[tuple[float, float, float]]:
    body = sample_line(rng, (0, -0.55, 0), (0, 0.55, 0), 900, 0.025)
    left = sample_ellipsoid(rng, (-0.55, 0.05, 0), (0.55, 0.42, 0.12), 4550)
    right = sample_ellipsoid(rng, (0.55, 0.05, 0), (0.55, 0.42, 0.12), 4550)
    return (body + left + right)[:POINT_COUNT]


def build_dragon(rng: random.Random) -> list[tuple[float, float, float]]:
    spine: list[tuple[float, float, float]] = []
    for _ in range(6200):
        t = rng.random()
        x = (t - 0.5) * 1.6
        y = math.sin(t * math.pi * 2.2) * 0.35 + t * 0.25 - 0.2
        z = math.cos(t * math.pi * 1.6) * 0.18
        x += (rng.random() - 0.5) * 0.05
        y += (rng.random() - 0.5) * 0.05
        z += (rng.random() - 0.5) * 0.05
        spine.append((x, y, z))
    wing_l = sample_ellipsoid(rng, (-0.35, 0.35, 0.05), (0.45, 0.28, 0.08), 1900)
    wing_r = sample_ellipsoid(rng, (0.25, 0.45, -0.05), (0.4, 0.22, 0.08), 1900)
    return (spine + wing_l + wing_r)[:POINT_COUNT]


def build_lily(rng: random.Random) -> list[tuple[float, float, float]]:
    center = sample_ellipsoid(rng, (0, 0, 0), (0.12, 0.12, 0.08), 1800)
    petals = sample_petals(rng, POINT_COUNT - 1800)
    return (center + petals)[:POINT_COUNT]


def write_obj(path: Path, points: list[tuple[float, float, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# Morphora placeholder point cloud — {len(points)} vertices\n")
        for x, y, z in points:
            f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")


def main() -> None:
    builders = {
        "butterfly_10k.obj": build_butterfly,
        "dragon_10k.obj": build_dragon,
        "lily_10k.obj": build_lily,
    }

    for name, builder in builders.items():
        rng = random.Random(SEED)
        points = builder(rng)
        if len(points) != POINT_COUNT:
            raise RuntimeError(f"{name}: expected {POINT_COUNT} points, got {len(points)}")
        out = OUT_DIR / name
        write_obj(out, points)
        print(f"Wrote {out} ({len(points)} points)")


if __name__ == "__main__":
    main()
