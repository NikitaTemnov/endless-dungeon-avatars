# Abyss Artist — staged narrative-scene illustration workflow (R1)

> **Scope:** This is the Artist chat's production workflow for **explicitly commissioned** correction/creation of past game scenes. It is **not** the game-master workflow for generating an illustration inside a player's gameplay turn. The two workflows share canonical facts, but have separate triggers, ownership and acceptance.

## Authority and data boundaries

1. **Source of truth:** live `Endless Dungeon - Text-Based RPG Game` sheets and the final confirmed in-game turn. Priority: current global visual/protocol rules → Skitalets species morphology and reviewed original pixels → hero's personal record → actual equipment and inventory → actual location, light and final action. User's scene prompt is a **candidate**, checked against those sources before use.
2. **No game changes:** Artist's illustration-only activity cannot change turn order, XP, RoF, health, inventory, loot, world layout, resources, hidden knowledge, or save-state.
3. **No public secrets:** snapshots, character inventories, undiscovered geography, reference downloads and actual prompt content stay in a private working context; do not commit them to public GitHub. This repository stores only generic tools, schemas and public process documentation.
4. **Non-applicability of old bans:** a prior broad rule that Artist should never produce *any* scene is superseded **only when** the user explicitly commissions a scene correction in Artist. Unrequested gameplay scenes remain owned by their gameplay chats. The separate ban on images of magical elements of orders III/IV remains in force.
5. Historical rejected renders, old generator prompts and obsolete local instructions are **audit data, not sources**. Quarantine them before scene assembly. Never overwrite authoritative turn history to erase a visual mistake.

## Strict stages / user gates

| Stage | Deliverable and exit gate |
|---|---|
| **0 · Normalize** | Resolve the **last two actual gameplay scenes** for each of the two requested heroes (Ilya and Thirteen), exclude non-turn service notes, identify four distinct IDs and previous failed visuals. Mark obsolete scene-local *art* instructions as quarantined (preserve audit); compile one current Artist-only rule set. **Do not generate.** Obtain user acceptance to proceed. |
| **1 · Four prompt passports** | For **each** of the four scenes, work general→specific: latest scene and local geometry; exact hero/race; original morphology pixels; actual worn gear/held items and left/right hands; symbiote's confirmed position or deliberately hidden attachment; diegetic light and visibility; forbidden/unconfirmed props; composition; final physical instant. Produce four distinct positive prompts, source citations, negative/postflight checklists and `scene_guard.py` snapshot checks. The proposed text must be traceable to cells. **Do not generate.** Obtain user acceptance. |
| **2 · Scene 1** | Preflight, generate **one** landscape artwork, inspect actual pixels, show result and exact departures, collect explicit **Approve** or **Revise** and free-text user comments. Do not proceed without approval. |
| **3 · Scene 2** | Same, only after Scene 1 approval. |
| **4 · Scene 3** | Same, only after Scene 2 approval. |
| **5 · Scene 4** | Same, only after Scene 3 approval. |
| **6 · Delivery** | Verify four individually approved originals and their IDs, make exactly those four available for download (and optionally a ZIP), with no rejected frames. |

**Every phase is one interactive task, not an unattended batch.** At each transition, show the Artist's canonical avatar, compact rounded narrative/status block, current progress and next action, and a real actionable **Continue** control. After an image, show **separate approval/revision actions and an optional free-text comments field**; user approval is never presumed.

## Prompt pipeline (fail closed)

1. Read live cell values and actual approved morphology/environment reference **pixels**. Archived/failed images are never positive visual inputs.
2. Construct a **private JSON scene snapshot** from current canonical sources. Use the PR's `tools/scene-prompt-guard/scene_guard.py` for static prompt contamination and light-distance checks. Keep prohibited concepts **outside the positive prompt** (in review checklists); never send a positive instruction that mentions prohibited HUD/gear/props as desired contents.
3. Compare the generated positive text **word for word** with the controlled request submitted to the image tool. If the tool may secretly rewrite or substitute the positive text, `generator_prompt_is_controllable=false`; the checker must **STOP**. Do not misreport the GitHub checker as controlling the model.
4. If controlled generation is available, produce **one single horizontal physical scene**, never a collage, HUD, character card or infographic.
5. Manually inspect the actual output: race/face/head proportions; clothing and headwear; open hands and right/left held items; symbiote count and attachment; dry/wet stone, chamber geometry and scale; light source and useful radius; unknown beyond the explored threshold; no external menus, stats or captions.
6. Failures: reject, preserve evidence and comments in an audit, amend the *private* scene passport, and re-run preflight. After **three rejected attempts** or repeated prompt substitution, stop this generator route and issue an Artist handoff. The count is local to the artwork; it does not reset just because the chat changed.
7. Only user-approved art may be labeled canonical, archived as final, or included in stage 6.

## Private scene handoffs

Artist may receive a detailed user-written scene prompt in the private chat. Store that draft and its exact canonical cell references only in the private production protocol, review it again during Stage 1, and never commit it or undisclosed game-state details to this public repository.

**Reference and tests:** [scene-prompt-guard README](README.md). This GitHub PR is a draft tool proposal, not a merged runtime policy or proof that any particular generation was accepted.
