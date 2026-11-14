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

See [ARTIST_WORKFLOW.md](ARTIST_WORKFLOW.md) for the separate **dynamic-length** commissioned-art pipeline (Stage 0 source validation, Stage 1 individual prompts, one image and user approval per later stage, final delivery of exactly the approved count). Newly reported gameplay turns must be verified in live canonical sources; previously accepted images must not be recreated. The game chat's own illustration-at-end-of-turn procedure is a different workflow. This checker is a **preflight aid**, not a generator or pixel auditor; it cannot bypass a hidden prompt rewrite. Do not put real character scene snapshots or non-public game state in this public repository.

## Locked approved prompt packages (Artist R3)

For approved artwork repair passes, **do not call** `positive_prompt()` to
reconstruct an already accepted text. Use the independent
[`locked_package_guard.py`](locked_package_guard.py) instead.

This optional path checks a private package directory containing:
- A scene manifest with the approved positive prompt SHA-256, ordered original
  PNG metadata/byte counts/hashes, and intended transport parameters.
- The exact approved UTF-8 prompt file and original reference PNG files.
- A separately reviewed *private attestation* binding scene/queue, canonical
  source-cell pointers, approved prompt hash, ordered PNG hashes, reference
  pixel review, and positive physical facts. No private artifacts belong here.

Offline use:

```bash
python tools/scene-prompt-guard/locked_package_guard.py /private/path/to/art-package
python -m unittest discover -s tools/scene-prompt-guard -p 'test_*.py' -v
```

The locked path imports the same forbidden-positive-term filter from
`scene_guard.py`, verifies manifest against attestation and original bytes,
and **never edits or regenerates prompt wording**. A physical light radius may
be declared `null` with status `unknown` where no exact figure is canonically
confirmed; it is not invented for a numeric guard. This is distinct from the
original structured-snapshot `positive_prompt()` path, which retains its
strict numeric radius requirement.

The program neither verifies Google Sheets freshness itself nor proves the
attestation is independently signed, the model received all bytes, or output
pixels meet canon. Those are separate source-review, transport and B219
acceptance gates. A private transport script must call `verify_package()`
**before** any permitted request; passing a static check never authorizes an
image-generation call. Public regression tests use synthetic data only.

## Historical scene binding and model-visible reference roles (R3)

The generic `scene_transport_guard.py` builds on `locked_package_guard.py`.
It runs **offline** and requires two independent private attestations:

- `historical_moment`: event ID equals the requested scene, the archived
  event-cell is the authority for equipment *state at that time*, and later
  events are excluded. A current equipment sheet may provide item definitions
  only, not override the archived pose or lantern state. Physical anchors and
  historical exclusions are checked against the locked approved prompt.
- `role_guidance`: a separately hashed UTF-8 text file enumerating each PNG's
  order, canonical reference cell, and role (`morphology`/`environment`).
  Its hash and ordered roles must match both the manifest and attestation.

Offline command: `python tools/scene-prompt-guard/scene_transport_guard.py /private/path/to/package`

The approved scene prompt file is **not rewritten**. A future Image API call
can send `role_guidance + '\n\n' + approved_prompt` as a single model-visible
text field. **This is an expanded effective request text**. It must be explicitly
approved for transmission; do not mistake retaining the approved prompt
substring for an unchanged entire API input. Filename-only or unrecognized
metadata are not valid role delivery mechanisms.

These checks are consistency tests, not verified connection to live canonical
sheets or a proof of model understanding. They never perform image generation.
Keep all real prompt text, references, event IDs, character state and the
complete private manifest/attestation outside this public repository.
