# Abyss Artist — staged narrative-scene illustration workflow (R2)

> **Scope:** Artist's private, explicitly commissioned correction/creation of previously played game scenes. This is **not** the game-master workflow for artwork inside a player's new gameplay turn.

## Source authority and boundaries

1. Ground each scene in the **final confirmed physical moment of its own in-game turn** from live `Endless Dungeon - Text-Based RPG Game` records; check changes after every prior snapshot.
2. Source order: global game and visual protocols → original Skitalets morphology reference **pixels** → character's species, personal appearance, current-at-that-turn equipment/inventory → that turn's physical outcome, location and visibility. A prompt, rejected picture, or obsolete art note never overrides game canon.
3. A user-confirmed **already accepted illustration** is excluded from the re-creation backlog, even if an older queue entry still says "rejected." Preserve the conflicting audit until the correct original and provenance are verified; do not silently override accepted art.
4. When the user reports a **new gameplay turn** but the source Sheets/chat record has not caught up, mark that scene `PENDING_SOURCE_SYNC`. Do not invent its event ID, physical outcome, location, count or equipment. Recheck the live canonical source before advancing.
5. Artist's illustration-only work does **not** change turns, XP, RoF, time, HP, world state, inventory, loot or hidden knowledge. A prior generic ban on Artist-produced scenes does not apply to explicit commissioned **repairs**, but the ban on depicting magic elements of orders III/IV remains.
6. Keep rejected prompt variants and old art interpretations as **quarantined audit records**, not executable instructions. Do not delete original game history or publicly publish private snapshots/scenes.

## Stage plan (scene count is dynamic)

Let `N` be the number of **unapproved, explicitly commissioned** scenes after the latest user corrections and canonical-source validation.

| Stage | Outcome / gate |
|---|---|
| **0 · Identify and quarantine** | Select exactly the requested **N** scenes, exclude already approved art and canceled/replayed turns, distinguish new gameplay turns from audits and unsuccessful image-generation attempts. Flag any unavailable latest turn as `PENDING_SOURCE_SYNC`; stage 0 remains open until all N IDs and their canonical sources are verified. Quarantine only old art/prompt instructions, not game history. **Do not generate.** |
| **1 · N private prompt passports** | Make one independent source-mapped scene passport and positive prompt per verified scene. Review general→specific: morphology pixel originals, hero's eyes/symbiote, exact equipment at the chosen moment, right and left hands, geometry, physical light and hidden knowledge. Run static guard preflight where feasible. **Do not generate.** Request user approval before creating the first frame. |
| **2 … N+1 · One image per stage** | Generate **one** landscape physical scene and inspect the actual pixels. Present **Approve** and **Revise** actions plus a free-text comments field. Do not proceed to the next image until the current one is explicitly approved. |
| **N+2 · Final delivery** | Verify **exactly N user-approved** individual original image files for download (optionally a ZIP), never rejected variants. |

**Example:** when the user commissions five unfinished scenes, stages are **0, 1, 2–6, 7**, with five independently approved images. The number changes if the user revises the requested set; do not keep the old four-image completion rule.

## Preflight and postflight (fail closed)

1. Obtain **live Sheets source values** and actually inspect approved morphology and environment reference **pixels**; do not mistake a URL or text description for a viewed image.
2. Build a private structured snapshot for *one* scene with event ID, source-cell provenance, appearance, worn gear, item in each hand, symbiote's confirmed attachment (or unknown), local light/visibility and permitted geometry. Never merge character snapshots from different turns.
3. Keep the **positive prompt** factual and self-contained. Store negative examples, historical bad prompts and QA restrictions separately. Use `scene_guard.py` only as static preflight; it does **not** control the image tool's hidden prompt or inspect output pixels.
4. If the generator's positive prompt is silently substituted and cannot be verified, record `generator_prompt_is_controllable=false` and **stop** rather than claiming static-guard success implies a correct image.
5. Inspect each output: artificial adult puppet-like Skitalets anatomy, face/mask and eyes, actual clothes, right/left held objects, symbiote count/location, light source/range, wet/dry stone and explored bounds. A visual mismatch is not canonical.
6. Reject and log errors; change the root cause before retrying. After three rejected attempts or repeated prompt substitution, stop that generator route and provide a controlled handoff. Do not reset this limit by changing chat.
7. Always display canonical Artist avatar, short narrative status, stage progress and a **real interactive action**. After each image, offer user approval, revision and free-text comments. Never infer approval from technical upload or a formerly rejected queue status.

## Private information

The GitHub repository is public; keep actual scene IDs, player actions, undiscovered geography, full prompts and inventory **out of GitHub**. Store the current project's five-scene selection and source pointers only in private Artist protocol. See [scene-prompt-guard README](README.md). This PR may remain Draft; merging it is a separate decision.
