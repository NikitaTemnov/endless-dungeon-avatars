# Artist cross-chat coordination · STANDARD ↔ WORK · v1 · 2026-11-11

## Purpose
Run the ordinary ChatGPT Artist chat (**STANDARD**) and ChatGPT Work Artist chat (**WORK**) in parallel without the repair of one chat breaking the other. This is a **documented workflow, not an automatic distributed lock or renderer patch**.

## Configuration ownership
| Surface | Shared or private? | Rule |
|---|---|---|
| Game's canonical Google Sheet, visuals, approved files | SHARED data | Live read is authoritative; only edit exact authorized cells after preflight; do not overwrite gameplay state from Artist |
| Artist avatar original, role terminology, visual category standards | SHARED baseline | Do not regenerate/mutate; changes require user approval |
| `ARTIST_UI_CONTRACT.md` | SHARED authoring baseline | Common stable rules only; chat-specific deviations live in profiles |
| `chat-profiles/STANDARD_CHAT_PROFILE.md` | STANDARD-owned | Ordinary chat edits in `chat-standard/*` branch; Work read-only |
| `chat-profiles/WORK_CHAT_PROFILE.md` | WORK-owned | Work edits in `chat-work/*` branch; STANDARD read-only except initial opt-in template |
| Individual chat's answers, UI state, local files and progress display | CHAT-LOCAL | Never infer or manipulate one from the other |
| Common Google Docs production protocol | SHARED historical record | Append small scoped changes, never wholesale replace, use requiredRevisionId when available |

## Concurrent edit protocol (human review)
1. Announce the **chat owner**, precise files/Sheets ranges, intent, and reason. Don't imply other chat has agreed.
2. Fetch current GitHub content and blob SHA / current Google Docs revision or exact Sheets values immediately before writing. If expected state changes, **abort and re-read**, never force overwrite.
3. Make chat-local edits in its own branch and folder. For shared GitHub files, propose changes via PR; **no automatic merge** or force-push to another chat's branch. For shared Docs, append a dated scope-tagged addendum with revision guard. For Sheets, avoid simultaneous writes to same cells; verify readback and stop on discrepancy.
4. Keep user approvals and existing originals intact. Source of truth for a specific game fact is live game sheet, not another conversation's summary. Never copy private campaign details to this public repo.
5. When both chats work on one queue, choose **separate rows/assets or sequential handoff**. Unique entity type + variant + category is an idempotency key. Confirm existing PNG/queue record first. If conflict or uncertain provenance, set `NEEDS_REVIEW` instead of generating or overwriting.
6. Review shared proposals with the user and merge explicitly. Until merge, cite the intended **branch and commit SHA**; do not pretend an unmerged file is universally active.
7. After any change, validate **in the affected chat** with a real reply. One chat's correct UI cannot prove the other's UI works.

## UI regression guard
- STANDARD: avatar once, outside cards; separate **real** narrative and status `<box>` components; native inputs/actions when needed. **Never use Unicode pseudographic borders** (`╭ │ ╰ ┌ ┐ └ ┘`) or Markdown `[1]` pseudo-radios in place of components.
- WORK: follow Work's product-supported interface, without pretending DIL controls are available; keep chat-specific presentation guidance in its profile.
- These Markdown files cannot change ChatGPT's system or client renderer. If a UI constraint cannot be met in the active surface, admit the limitation rather than draw counterfeit controls.

## Escalation
If there is an apparent mismatch: STOP writes to shared targets → compare source revision, chat profile and explicit last user decision → propose a narrow patch in owned branch → verify in correct chat → ask for user review of any shared merge.

## Links
- Common contract: `ARTIST_UI_CONTRACT.md`
- Standard profile: `chat-profiles/STANDARD_CHAT_PROFILE.md`
- Work profile: `chat-profiles/WORK_CHAT_PROFILE.md`
- Common workflow: `ARTIST_WORKFLOW.md`
