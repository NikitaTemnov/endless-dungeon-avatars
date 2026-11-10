# Scene prompt guard (Endless Dungeon)

This is a **fail-closed** standard-library Python checker for **narrative physical scene** prompts, not general UI, icons, or gameplay. It helps keep image instructions isolated from text RPG reports.

## Status and limits

- The Google Sheet remains the source of truth. Populate a JSON snapshot from the **current** character, equipment, final pose, room and lighting. Do not copy archived full responses into it.
- This tool checks required source references, selected physical fields, forbidden prompt contamination, and range of useful illumination. It builds a positive scene-only text and a handoff after 3 failed images.
- It **does not connect to Google Sheets or the image model**, read images, verify real references, guarantee a generator has received the same text, or validate output pixels.
- When a generator has an inaccessible/re-written positive prompt, set `generator_prompt_is_controllable=false`; the script refuses a new generation.
- A handoff document can still be generated after three failed images or the blocked flow.
- Keep actual secret game state out of this public repository. Make scene snapshots outside GitHub.

## Local usage

```bash
python tools/scene-prompt-guard/scene_guard.py scene.json
python tools/scene-prompt-guard/scene_guard.py scene.json --failures 3
python -m unittest discover -s tools/scene-prompt-guard -p 'test_*.py' -v
```

The JSON schema is implicit in the `validate` function. It demands `category=scene`, `race_profile=adult_biosynthetic_skitalets`, `style_profile=cinematic_aaa_dark_fantasy_pbr`, sources for character/equipment/pose/location/lighting, reference URLs and `pixels_reviewed=true`, actual physical details, and reasonable light radius.

Generated text is **not** proof of canon. The next gate is to examine the **actual sent generator prompt**, if accessible, and the real output pixels. The current ChatGPT image tool can rewrite prompts; this script cannot override that.

## Explicit Abyss Artist scene-correction workflow

See [ARTIST_WORKFLOW.md](ARTIST_WORKFLOW.md) for the separate **Stage 0–6** commissioned-art pipeline, user approval after **each** of four scenes, contextual isolation from gameplay responses, and final four-image delivery. The game chat's own illustration-at-end-of-turn procedure is a different workflow. This checker is a **preflight aid**, not a generator or pixel auditor; it cannot bypass a hidden prompt rewrite. Do not put real character scene snapshots or non-public game state in this public repository.
