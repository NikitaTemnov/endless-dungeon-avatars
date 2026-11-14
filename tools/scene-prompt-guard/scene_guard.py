#!/usr/bin/env python3
"""Fail-closed validator for Endless Dungeon narrative scene prompts.

Only prepares a controlled positive text. It never generates images, contacts
Google Sheets, accesses hidden image-model prompts, or verifies output pixels.
"""
import argparse
import json
import re
import sys
from pathlib import Path

RACE = "adult_biosynthetic_skitalets"
STYLE = "cinematic_aaa_dark_fantasy_pbr"
BAD = re.compile(
    r"(?i)\b(?:hud|dashboard|rpg\s*ui|game\s*interface|"
    r"narrative\s*panels?|text\s*overlay|status\s*panel|"
    r"tactical\s*(?:gear|vest|pouch)|helmet|chibi|super.deformed|"
    r"human\s*(?:explorer|adventurer)|wet\s*floor|"
    r"glowing\s*mineral\s*deposits?)\b|"
    r"(?:интерфейс\s*игры|игров(?:ая|ой|ые)\s*панел|"
    r"тактическ(?:ая|ий|ие)\s*(?:форм|подсум)|чиби|шлем)"
)
SOURCE_FIELDS = ("character", "equipment", "pose", "location", "lighting")


class Reject(ValueError):
    """The next generator call MUST NOT happen."""


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise Reject(f"Missing: {label}")
    if BAD.search(value):
        raise Reject(f"Forbidden positive concept in: {label}")
    return value.strip()


def texts(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from texts(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from texts(item)


def validate(snapshot, *, require_control=True):
    if not isinstance(snapshot, dict):
        raise Reject("Snapshot must be a JSON object")
    if (snapshot.get("category") != "scene"
            or snapshot.get("race_profile") != RACE
            or snapshot.get("style_profile") != STYLE):
        raise Reject("Wrong category, species or style preset")
    if require_control and snapshot.get("generator_prompt_is_controllable") is not True:
        raise Reject("Cannot control the actual submitted positive image prompt")
    for key in ("hero", "scene_id", "final_moment"):
        text(snapshot.get(key), key)
    source = snapshot.get("sources")
    if not isinstance(source, dict) or any(
        not isinstance(source.get(key), str) or not source[key].strip()
        for key in SOURCE_FIELDS
    ):
        raise Reject("All source fields must cite an exact canonical cell")
    refs = snapshot.get("references")
    if not isinstance(refs, dict) or refs.get("pixels_reviewed") is not True:
        raise Reject("Approved original image pixels were not reviewed")
    for key in ("morphology", "environment"):
        links = refs.get(key)
        if not isinstance(links, list) or not links or any(
            not isinstance(link, str) or not link.startswith("https://")
            for link in links
        ):
            raise Reject(f"Missing original reference links: {key}")
    character = snapshot.get("character")
    pose = snapshot.get("pose")
    location = snapshot.get("location")
    lighting = snapshot.get("lighting")
    if not all(isinstance(x, dict) for x in (character, pose, location, lighting)):
        raise Reject("Missing character, pose, location or light")
    for key in ("body", "face", "eyes"):
        text(character.get(key), f"character.{key}")
    for key in ("stance", "right_hand", "left_hand"):
        text(pose.get(key), f"pose.{key}")
    for key in ("name", "near_geometry", "far_geometry"):
        text(location.get(key), f"location.{key}")
    text(lighting.get("source"), "lighting.source")
    radius = lighting.get("useful_radius_m")
    if not isinstance(radius, (int, float)) or not (0 < radius <= 100):
        raise Reject("Invalid physical light radius")
    if lighting.get("background") not in ("dark", "visible"):
        raise Reject("Unknown background visibility")
    gear = snapshot.get("equipment")
    if not isinstance(gear, list) or not gear:
        raise Reject("Actual equipped items are required")
    for item in gear:
        text(item, "equipment")
    props = snapshot.get("visible_props", [])
    if not isinstance(props, list):
        raise Reject("visible_props must be a list")
    for prop in props:
        if not isinstance(prop, dict):
            raise Reject("Malformed visible object")
        text(prop.get("description"), "visible prop")
        text(prop.get("source"), "visible prop source")
        distance = prop.get("distance_m")
        if not isinstance(distance, (float, int)) or distance < 0:
            raise Reject("Visible object needs a grounded distance")
        if distance > radius and not prop.get("silhouette_only", False):
            raise Reject("Detailed object beyond useful light radius")
    if any(BAD.search(value) for value in texts(snapshot)):
        raise Reject("Forbidden prompt contamination in scene snapshot")


def positive_prompt(snapshot, *, require_control=True):
    validate(snapshot, require_control=require_control)
    c, p = snapshot["character"], snapshot["pose"]
    l, light = snapshot["location"], snapshot["lighting"]
    props = ", ".join(x["description"] for x in snapshot.get("visible_props", []))
    props = props or "the physically confirmed nearby stone forms"
    return (
        "One uninterrupted cinematic physical moment, AAA dark-fantasy PBR "
        "environment, mature anatomy, high-end stylized realism. "
        "An adult, artificial biosynthetic Skitalets with a smooth pale shell, "
        "a sculpted facial mask and fine dark fibrous joint gaps. "
        f"Body: {c['body']}. Face: {c['face']}. Eyes: {c['eyes']}. "
        f"Actually worn clothing: {', '.join(snapshot['equipment'])}. "
        f"Final pose: {p['stance']}. Right hand: {p['right_hand']}. "
        f"Left hand: {p['left_hand']}. "
        f"Physical location: {l['name']}; nearby {l['near_geometry']}; "
        f"farther {l['far_geometry']}. "
        f"Visible physical objects: {props}. "
        f"Light source: {light['source']}, useful radius "
        f"{light['useful_radius_m']:g} meters; background {light['background']}. "
        f"Exact final instant: {snapshot['final_moment']}. "
        "An entirely diegetic composition with physically motivated light."
    )


def artist_handoff(snapshot, failures, reason):
    if failures < 3:
        raise Reject("Artist handoff is required after three rejected attempts")
    # An UNCONTROLLABLE generator is the reason to hand off; it must not stop
    # creation of a non-executing prompt for the separately controlled artist.
    prompt = positive_prompt(snapshot, require_control=False)
    ref = snapshot["references"]
    return (
        f"# Художник — Endless Dungeon — {snapshot['hero']}\n\n"
        f"Нарисовать один заключительный физический момент события "
        f"{snapshot['scene_id']}. Это иллюстрация, не новый ход.\n\n"
        f"## Положительное задание\n\n{prompt}\n\n"
        f"## Утверждённые оригиналы\n\n"
        f"Вид и пропорции: {', '.join(ref['morphology'])}\n\n"
        f"Среда (лишь стиль материалов): {', '.join(ref['environment'])}\n\n"
        f"## Источники фактов\n\n"
        f"{json.dumps(snapshot['sources'], ensure_ascii=False, indent=2)}\n\n"
        f"## Приёмка\n\nПроверить оригинальные пиксели, зрелые пропорции, "
        f"лицо-маску, экипировку, обе руки, фактическую геометрию, "
        f"радиус света и отсутствие внешних игровых карточек. "
        f"Не утверждать непроверенный кадр; не менять игру.\n\n"
        f"Попыток отказа: {failures}. Причина передачи: {reason}.\n"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--failures", type=int, default=0)
    parser.add_argument("--prompt-file", type=Path, default=Path("scene-prompt.txt"))
    parser.add_argument("--artist-file", type=Path, default=Path("artist-handoff.md"))
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        if args.failures >= 3:
            handoff = artist_handoff(snapshot, args.failures, "failed pixel audit or prompt substitution")
            args.artist_file.write_text(handoff, encoding="utf-8")
            print(f"STOP / HANDOFF: {args.artist_file}")
            return 0
        prompt = positive_prompt(snapshot)
        args.prompt_file.write_text(prompt + "\n", encoding="utf-8")
        print(f"PRECHECK PASSED: {args.prompt_file}")
        return 0
    except (Reject, OSError, json.JSONDecodeError) as error:
        print(f"STOP: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
