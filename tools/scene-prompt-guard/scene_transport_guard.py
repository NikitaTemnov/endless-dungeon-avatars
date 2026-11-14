#!/usr/bin/env python3
"""Fail-closed historical-scene and reference-role transport preflight.

This is a generic, public-safe checker. Real scene facts, reference pixels and
approval records belong in a PRIVATE package. Does not use networks or generate.
"""
import hashlib
import json
from pathlib import Path
import re
import sys

from scene_guard import BAD, Reject
from locked_package_guard import verify_package, _file


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _phrase(text, phrase):
    return re.search(r'(?<!\w)' + re.escape(phrase) + r'(?!\w)', text, flags=re.IGNORECASE) is not None


def verify_transport_package(folder):
    """Return (manifest, approved_prompt, images, transport_prompt) or reject.

    Historical attestation and role wording are checked, but are not proof of
    fresh canonical-source retrieval or model adherence. Approved prompt bytes
    remain unchanged. Model-visible role instructions are a SEPARATE preface.
    """
    folder = Path(folder).resolve()
    manifest, prompt, images = verify_package(folder)
    proof = json.loads(_file(folder, 'artist_guard_attestation.json').read_text(encoding='utf-8'))
    historical = proof.get('historical_moment')
    if not isinstance(historical, dict) or historical.get('kind') != 'historical_final_moment':
        raise Reject('Missing historical final-moment authority')
    scene = manifest['scene_id']
    anchor = historical.get('source_cell')
    if historical.get('event_id') != scene or not isinstance(anchor, str) or '!' not in anchor:
        raise Reject('Historical source/event differs from scene ID')
    if historical.get('equipment_state_source_cell') != anchor or anchor not in proof['source_cells']['pose']:
        raise Reject('Historical equipment authority must be the same archived event')
    definition_sources = historical.get('definition_sources_only')
    if not isinstance(definition_sources, list) or not definition_sources or any(
        not isinstance(source, str) or '!' not in source for source in definition_sources
    ):
        raise Reject('Equipment definition sources must be listed separately from historical state')
    later_ids = historical.get('excluded_later_event_ids')
    if not isinstance(later_ids, list) or not later_ids or scene in later_ids or len(set(later_ids)) != len(later_ids):
        raise Reject('Later scene-state exclusions are missing or invalid')
    facts = historical.get('physical_positive_anchors')
    if not isinstance(facts, dict) or len(facts) < 3 or any(
        not isinstance(key, str) or not isinstance(value, str) or not value or not _phrase(prompt, value)
        for key, value in facts.items()
    ):
        raise Reject('Historical physical facts not independently anchored in approved scene text')
    exclusions = historical.get('forbidden_later_phrases')
    if not isinstance(exclusions, list) or not exclusions or any(
        not isinstance(s, str) or not s or _phrase(prompt, s) for s in exclusions
    ):
        raise Reject('Later equipment or scene-state contamination')
    role_info = manifest.get('role_guidance')
    approved_role = proof.get('role_guidance')
    if not isinstance(role_info, dict) or not isinstance(approved_role, dict):
        raise Reject('Reference-role guidance must be declared and reviewed')
    role_hash = role_info.get('sha256')
    if not isinstance(role_hash, str) or not re.fullmatch('[0-9a-f]{64}', role_hash) or role_hash != approved_role.get('sha256'):
        raise Reject('Reference-role instruction hash differs from review')
    raw = _file(folder, role_info.get('file')).read_bytes()
    if digest(raw) != role_hash:
        raise Reject('Reference-role instructions changed')
    try:
        role_text = raw.decode('utf-8')
    except UnicodeError as exc:
        raise Reject('Reference-role instructions must be UTF-8') from exc
    if not role_text.strip() or BAD.search(role_text):
        raise Reject('Unsafe or empty role guidance')
    approved_map = approved_role.get('ordered_roles')
    if not isinstance(approved_map, list) or len(approved_map) != len(images):
        raise Reject('Incomplete independent reference-role map')
    for number, ((item, _), ref) in enumerate(zip(images, approved_map), start=1):
        if not isinstance(ref, dict) or (ref.get('cell'), ref.get('role')) != (item['cell'], item['role']):
            raise Reject('Original reference role or order changed')
        marker = f'Image {number} ({item["cell"]}): {item["role"]}.'
        if role_text.count(marker) != 1:
            raise Reject('Role guidance omits/duplicates an original image label: ' + item['cell'])
    transport_prompt = role_text.rstrip('\r\n') + '\n\n' + prompt
    if transport_prompt.count(prompt) != 1 or len(transport_prompt) > 32000:
        raise Reject('Approved prompt not embedded intact, or transport text oversize')
    if proof.get('reference_role_transport_mode') != 'locked_preface_and_originals':
        raise Reject('Model-visible reference-role transport not explicitly selected')
    return manifest, prompt, images, transport_prompt


def main():
    import argparse
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('folder', type=Path)
    args = cli.parse_args()
    try:
        manifest, prompt, images, transport = verify_transport_package(args.folder)
        print(json.dumps({
            'status': 'OFFLINE_PASS_NO_API_CALL', 'scene': manifest['scene_id'],
            'prompt_sha256': digest(prompt.encode('utf-8')),
            'image_count': len(images), 'transport_prompt_sha256': digest(transport.encode('utf-8')),
            'note': 'Transport adds a separately hashed role preface; approved scene text unchanged.'
        }, ensure_ascii=False, indent=2))
        return 0
    except (Reject, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print('STOP:', exc, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
