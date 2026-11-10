#!/usr/bin/env python3
"""Offline, fail-closed bridge for an approved Artist prompt package.

This checks the *existing* prompt bytes and original PNG bytes without rewriting
any physical scene content. Keep private manifests, attestations, and art outside
public GitHub. No network access, image generation, or canonical-source fetching.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from scene_guard import BAD, Reject

HASH = re.compile(r"[0-9a-f]{64}\Z")
CELL = re.compile(r"[A-Z]{1,3}[1-9][0-9]*\Z")
SOURCES = ("character", "equipment", "pose", "location", "lighting")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _file(folder, filename):
    if not isinstance(filename, str) or not filename or filename != Path(filename).name \
            or filename in (".", "..") or "/" in filename or "\\" in filename:
        raise Reject("Unsafe or missing package file name")
    path = folder / filename
    if not path.is_file() or path.is_symlink():
        raise Reject("Missing or unsafe package file: " + filename)
    return path


def verify_package(folder, manifest_name="artist_scene1_manifest.json",
                   attestation_name="artist_guard_attestation.json"):
    """Return validated (manifest, prompt, ordered [(item, raw_png)]) or STOP.

    Attestation is PRIVATE human-reviewed evidence, not proof of live Sheets or
    an external generator's internal handling. Does not run the generator.
    """
    folder = Path(folder).resolve()
    try:
        manifest = json.loads(_file(folder, manifest_name).read_text(encoding="utf-8"))
        proof = json.loads(_file(folder, attestation_name).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Reject("Cannot read manifest/attestation") from exc
    if not isinstance(manifest, dict) or not isinstance(proof, dict):
        raise Reject("Manifest and attestation must be objects")
    if not isinstance(manifest.get("protocol"), str) or not manifest["protocol"].startswith("ARTIST-SCENE-"):
        raise Reject("Wrong Artist protocol")
    scene_id = manifest.get("scene_id")
    if not isinstance(scene_id, str) or not scene_id or scene_id != proof.get("scene_id"):
        raise Reject("Scene ID differs from private source attestation")
    row = manifest.get("queue_row")
    if not isinstance(row, int) or isinstance(row, bool) or row < 1 or row != proof.get("queue_row"):
        raise Reject("Scene queue row mismatch")
    if proof.get("reviewed_live_sources") is not True or proof.get("pixels_reviewed") is not True:
        raise Reject("Live scene and original pixels have not been attested")
    refs = proof.get("source_cells")
    if not isinstance(refs, dict) or any(not isinstance(refs.get(k), str) or "!" not in refs[k]
                                         for k in SOURCES):
        raise Reject("Missing exact canonical source-cell references")
    light = proof.get("lighting_radius_m")
    if light is not None and (not isinstance(light, (int, float)) or isinstance(light, bool)
                              or not 0 < light <= 100):
        raise Reject("Unconfirmed or invalid light radius")
    if proof.get("lighting_radius_status") != ("unknown" if light is None else "confirmed"):
        raise Reject("Lighting radius provenance mismatch")
    locked_hash = manifest.get("prompt_sha256")
    if not isinstance(locked_hash, str) or not HASH.fullmatch(locked_hash) \
            or locked_hash != proof.get("approved_prompt_sha256"):
        raise Reject("Prompt hash does not match independent approval")
    prompt_raw = _file(folder, manifest.get("prompt_file")).read_bytes()
    if _digest(prompt_raw) != locked_hash:
        raise Reject("Locked approved prompt bytes changed")
    try:
        prompt = prompt_raw.decode("utf-8")
    except UnicodeError as exc:
        raise Reject("Prompt must be exact UTF-8") from exc
    if not prompt.strip() or len(prompt) > 32000 or BAD.search(prompt):
        raise Reject("Empty/oversize/contaminated positive prompt")
    phrases = proof.get("required_positive_phrases")
    if not isinstance(phrases, list) or len(phrases) < 3 or any(
        not isinstance(p, str) or not p or re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", prompt) is None for p in phrases
    ):
        raise Reject("Approved scene detail missing from locked positive prompt")
    images = manifest.get("references")
    if not isinstance(images, list) or not 1 <= len(images) <= 16:
        raise Reject("Invalid reference-image count")
    approved_hashes = proof.get("reference_sha256")
    approved_cells = proof.get("ordered_reference_cells")
    if not isinstance(approved_hashes, dict) or not isinstance(approved_cells, list) \
            or len(approved_cells) != len(images):
        raise Reject("Missing private reference approval")
    actual = []
    cells = set()
    roles = set()
    for idx, item in enumerate(images):
        if not isinstance(item, dict) or not isinstance(item.get("cell"), str) \
                or not CELL.fullmatch(item["cell"]) or item["cell"] in cells:
            raise Reject("Invalid, duplicate or missing original reference cell")
        cell = item["cell"]
        cells.add(cell)
        if cell != approved_cells[idx] or item.get("sha256") != approved_hashes.get(cell):
            raise Reject("Reference order/hash differs from approved originals: " + cell)
        if item.get("role") not in ("morphology", "environment"):
            raise Reject("Reference role is not approved: " + cell)
        roles.add(item["role"])
        if not isinstance(item.get("drive_id"), str) or not item["drive_id"]:
            raise Reject("Missing original Drive ID: " + cell)
        raw = _file(folder, item.get("filename")).read_bytes()
        if not raw.startswith(PNG_MAGIC) or len(raw) < 32 or len(raw) > 50 * 1024 * 1024:
            raise Reject("Invalid source PNG: " + cell)
        if not isinstance(item.get("bytes"), int) or item["bytes"] != len(raw) \
                or _digest(raw) != item.get("sha256"):
            raise Reject("Original reference bytes have changed: " + cell)
        actual.append((item, raw))
    if roles != {"morphology", "environment"} or set(approved_hashes) != cells:
        raise Reject("Missing reference role or mismatch in approved originals")
    if manifest.get("quality") not in ("low", "medium", "high", "xhigh", "max") \
            or not isinstance(manifest.get("model"), str) or not manifest["model"].startswith("gpt-image-") \
            or not isinstance(manifest.get("size"), str) or not re.fullmatch(r"[1-9][0-9]*x[1-9][0-9]*", manifest["size"]):
        raise Reject("Invalid model, quality or size fields")
    return manifest, prompt, actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("--manifest", default="artist_scene1_manifest.json")
    parser.add_argument("--attestation", default="artist_guard_attestation.json")
    args = parser.parse_args()
    try:
        manifest, prompt, images = verify_package(args.package_dir, args.manifest, args.attestation)
        print("PASS / OFFLINE ONLY:", manifest["protocol"], len(images), "PNG references, locked prompt",
              _digest(prompt.encode("utf-8")))
        return 0
    except (Reject, OSError, ValueError) as exc:
        print("STOP:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
