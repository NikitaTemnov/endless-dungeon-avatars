"""Purely synthetic offline regression tests for historical B218 transport."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scene_guard import Reject
from scene_transport_guard import verify_transport_package


def sha(value):
    return hashlib.sha256(value).hexdigest()


class SceneTransportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.prompt = b'Adult puppet stands with a bare right hand holding a spear, a bare left hand holding an unlit lantern, and a wooden targe.'
        self.png = b'\x89PNG\r\n\x1a\n' + bytes(range(40))
        refs = []
        for cell, role in [('D96', 'morphology'), ('D91', 'environment')]:
            f = 'test_' + cell + '.png'
            (self.folder / f).write_bytes(self.png)
            refs.append({'cell': cell, 'role': role, 'filename': f, 'drive_id': 'test-' + cell,
                         'bytes': len(self.png), 'sha256': sha(self.png)})
        (self.folder/'prompt.txt').write_bytes(self.prompt)
        self.roles = '\n'.join([
            'Reference image roles:',
            'Image 1 (D96): morphology.',
            'Image 2 (D91): environment.',
            'Image 1 contributes puppet morphology.',
            'Image 2 contributes stone PBR material quality.',
        ]) + '\n'
        (self.folder/'role.txt').write_text(self.roles, encoding='utf-8')
        self.manifest = {'protocol': 'ARTIST-SCENE-R3', 'scene_id': 'EXAMPLE-001',
                         'queue_row': 9, 'prompt_file': 'prompt.txt',
                         'prompt_sha256': sha(self.prompt), 'references': refs,
                         'model': 'gpt-image-2.5-sunburst', 'quality': 'high', 'size': '1536x1024',
                         'role_guidance': {'file': 'role.txt', 'sha256': sha(self.roles.encode())}}
        self.proof = {'scene_id': 'EXAMPLE-001', 'queue_row': 9,
                      'reviewed_live_sources': True, 'pixels_reviewed': True,
                      'source_cells': {k: "'Notes'!C3" for k in ('character', 'equipment', 'pose', 'location', 'lighting')},
                      'lighting_radius_m': None, 'lighting_radius_status': 'unknown',
                      'approved_prompt_sha256': sha(self.prompt),
                      'ordered_reference_cells': [r['cell'] for r in refs],
                      'reference_sha256': {r['cell']: r['sha256'] for r in refs},
                      'required_positive_phrases': ['Adult puppet', 'bare right hand', 'unlit lantern'],
                      'reference_role_transport_mode': 'locked_preface_and_originals',
                      'role_guidance': {'sha256': sha(self.roles.encode()),
                                        'ordered_roles': [{k: r[k] for k in ('cell', 'role')} for r in refs]},
                      'historical_moment': {'kind': 'historical_final_moment',
                                            'event_id': 'EXAMPLE-001',
                                            'source_cell': "'Notes'!C3",
                                            'equipment_state_source_cell': "'Notes'!C3",
                                            'definition_sources_only': ["'Equipment'!B7"],
                                            'excluded_later_event_ids': ['EXAMPLE-002'],
                                            'physical_positive_anchors': {'right': 'bare right hand',
                                                                          'left': 'unlit lantern',
                                                                          'shield': 'wooden targe'},
                                            'forbidden_later_phrases': ['lit lantern', 'left hand free']}}
        self.save()

    def save(self):
        (self.folder / 'artist_scene1_manifest.json').write_text(json.dumps(self.manifest), encoding='utf8')
        (self.folder / 'artist_guard_attestation.json').write_text(json.dumps(self.proof), encoding='utf8')

    def verify(self):
        return verify_transport_package(self.folder)

    def test_valid_transport_preserves_original_approved_prompt(self):
        m, original, images, transport = self.verify()
        self.assertEqual(original.encode(), self.prompt)
        self.assertEqual(transport.count(original), 1)
        self.assertTrue(transport.endswith(original))
        self.assertIn('Image 2 (D91): environment.', transport)
        self.assertEqual(len(images), 2)

    def test_wrong_historical_event_id_stops(self):
        self.proof['historical_moment']['event_id'] = 'EXAMPLE-002'; self.save()
        with self.assertRaises(Reject): self.verify()

    def test_missing_historical_equipment_anchor_stops(self):
        self.proof['historical_moment']['equipment_state_source_cell'] = "'Equipment'!B7"; self.save()
        with self.assertRaises(Reject): self.verify()

    def test_only_late_equipment_state_stops(self):
        self.proof['source_cells']['pose'] = "'Equipment'!B7"; self.save()
        with self.assertRaises(Reject): self.verify()

    def test_removed_history_facts_stops(self):
        self.proof['historical_moment']['physical_positive_anchors']['left'] = 'lit lantern'; self.save()
        with self.assertRaises(Reject): self.verify()

    def test_later_phrase_even_if_unlit_substring_does_not_trigger(self):
        self.assertIn('unlit lantern', self.verify()[1])

    def test_role_image_reorder_stops(self):
        self.proof['role_guidance']['ordered_roles'].reverse(); self.save()
        with self.assertRaises(Reject): self.verify()

    def test_missing_model_visible_label_stops(self):
        altered = self.roles.replace('Image 2 (D91): environment.', 'Environment reference.')
        (self.folder/'role.txt').write_text(altered, encoding='utf8')
        newhash = sha(altered.encode())
        self.manifest['role_guidance']['sha256'] = newhash
        self.proof['role_guidance']['sha256'] = newhash
        self.save()
        with self.assertRaises(Reject): self.verify()

    def test_role_text_change_stops(self):
        (self.folder/'role.txt').write_text(self.roles+'changed', encoding='utf8')
        with self.assertRaises(Reject): self.verify()

    def test_hud_role_contamination_stops(self):
        bad = self.roles + 'HUD\n'
        (self.folder/'role.txt').write_text(bad, encoding='utf8')
        self.manifest['role_guidance']['sha256'] = sha(bad.encode())
        self.proof['role_guidance']['sha256'] = sha(bad.encode())
        self.save()
        with self.assertRaises(Reject): self.verify()

    def test_wrong_transport_mode_stops(self):
        self.proof['reference_role_transport_mode'] = 'filename_only'; self.save()
        with self.assertRaises(Reject): self.verify()

    def test_missing_role_guidance_stops(self):
        del self.manifest['role_guidance']; self.save()
        with self.assertRaises(Reject): self.verify()

    def test_forbidden_later_action_stops(self):
        self.proof['historical_moment']['forbidden_later_phrases'] = ['wooden targe']; self.save()
        with self.assertRaises(Reject): self.verify()

    def test_missing_exclusion_stops(self):
        self.proof['historical_moment']['excluded_later_event_ids'] = []; self.save()
        with self.assertRaises(Reject): self.verify()

    def test_reference_file_bytes_changed_stops(self):
        (self.folder/'test_D91.png').write_bytes(self.png+b'tamper')
        with self.assertRaises(Reject): self.verify()

    def test_rewrite_approved_prompt_stops(self):
        (self.folder/'prompt.txt').write_bytes(self.prompt+b' altered')
        with self.assertRaises(Reject): self.verify()


if __name__ == '__main__':
    unittest.main()
