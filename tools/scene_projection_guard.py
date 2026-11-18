#!/usr/bin/env python3
"""Endless Dungeon: deterministic preflight for diegetic symbiote projections.

Checks structured scene snapshots BEFORE native image generation. Does not call
image models and cannot independently prove what the image model renders.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from typing import Any

KIND = "DIEGETIC_INFO_WINDOW"
AMBIGUOUS_BURUNDUK = re.compile(r"\b(?:проекция|образ|фигурка|силуэт)\s+Бурундук[а-я]*\b", re.I)
ANIMAL_VISUAL = re.compile(
    r"\b(?:белк[аиуой]|звер[ёья]|животн(?:ое|ого)|chipmunk|squirrel|animal\s+avatar)\b",
    re.I,
)

def validate(snapshot: dict[str, Any]) -> list[str]:
    """Return blocking errors; an empty list means prompt preflight passed."""
    errors: list[str] = []
    hero = str(snapshot.get("hero", "")).strip()
    symbiote = snapshot.get("symbiote") or {}
    projection = snapshot.get("projection") or {}
    if not hero:
        errors.append("Missing hero identity")
    if not str(symbiote.get("name", "")).strip():
        errors.append("Missing symbiote name")
    if not str(symbiote.get("anchor", "")).strip():
        errors.append("Missing symbiote physical anchor")
    if not isinstance(projection.get("active"), bool):
        errors.append("Projection active must be an explicit boolean")
    if projection.get("active") is not True:
        return errors
    if projection.get("kind") != KIND:
        errors.append("Active system projection must be DIEGETIC_INFO_WINDOW")
    if projection.get("shape") not in {"GEOMETRIC_PANEL", "GEOMETRIC_WINDOW"}:
        errors.append("System projection requires geometric information panel")
    if not str(projection.get("color", "")).strip():
        errors.append("Missing personal projection color")
    try:
        distance = float(projection.get("distance_m"))
        if not 0 <= distance <= 0.5:
            errors.append("Basic system window must be within 0.5 m of symbiote")
    except (TypeError, ValueError):
        errors.append("Missing numeric distance_m")
    if hero.casefold() == "скалоглав":
        if str(symbiote.get("name", "")).casefold() != "бурундук":
            errors.append("Skaloglav symbiote identity mismatch")
        if str(symbiote.get("anchor", "")).upper() != "FOREHEAD_CRYSTAL":
            errors.append("Skaloglav projection must be anchored at forehead crystal")
        if str(projection.get("color", "")).lower() not in {"green", "зелёный", "зеленый"}:
            errors.append("Skaloglav information window must be green")
        try:
            light = float(projection.get("light_radius_m"))
            if not 1 <= light <= 2:
                errors.append("Skaloglav weak illumination must be 1–2 m")
        except (TypeError, ValueError):
            errors.append("Missing numeric light_radius_m")
    visual = str(snapshot.get("visual_description", ""))
    if AMBIGUOUS_BURUNDUK.search(visual):
        errors.append("Ambiguous name-based projection: specify information window instead")
    if ANIMAL_VISUAL.search(visual):
        errors.append("Animal/creature description in the visual projection field")
    return errors

def positive_fragment(snapshot: dict[str, Any]) -> str:
    """Construct a positive-only scene fragment without names that imply animals."""
    errors = validate(snapshot)
    if errors:
        raise ValueError("Scene preflight failed: " + "; ".join(errors))
    if not snapshot["projection"]["active"]:
        return ""
    p = snapshot["projection"]
    return (
        f"A compact translucent {p['color']} GEOMETRIC ENERGY INFORMATION WINDOW, "
        "rectangular holographic interface panel with thin luminous lines and "
        "abstract non-readable symbols, physically floating beside the symbiote "
        f"at a distance of {float(p['distance_m']):.2f} m, with correct 3D "
        "perspective and realistic occlusion. This is an IN-WORLD SYSTEM INTERFACE "
        "with a weak local glow, not an external screen overlay."
    )

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scene_projection_guard.py scene_snapshot.json", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        print(positive_fragment(data))
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as err:
        print(f"BLOCKED: {err}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
