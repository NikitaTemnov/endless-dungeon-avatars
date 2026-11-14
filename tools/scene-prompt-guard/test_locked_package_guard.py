"""Synthetic-only regression tests; no private game assets or image-generation calls."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scene_guard import Reject
from locked_package_guard import verify_package


def h(data):
    return hashlib.sha256(data).hexdigest()


class LockedPackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.prompt = b"Adult white puppet Skitalets with golden eyes; right hand bronze spear; left hand unlit lantern."
        self.png = b"\x89PNG\r\n\x1a\n" + bytes(range(40))
        self.images = []
        for cell, role in (("D96", "morphology"), ("D91", "environment")):
            file = f"reference_{cell}.png"
            (self.folder / file).write_bytes(self.png)
            self.images.append({"cell": cell, "role": role, "filename": file,
                                "drive_id": "test-id-" + cell, "bytes": len(self.png),
                                "sha256": h(self.png)})
        (self.folder / "positive.txt").write_bytes(self.prompt)
        self.manifest = {"protocol": "ARTIST-SCENE-R3", "scene_id": "TEST-SCENE",
                         "queue_row": 4, "prompt_file": "positive.txt",
                         "prompt_sha256": h(self.prompt), "references": self.images,
                         "model": "gpt-image-2.5-sunburst", "quality": "high", "size": "1536x1024"}
        self.proof = {"scene_id": "TEST-SCENE", "queue_row": 4,
                      "reviewed_live_sources": True, "pixels_reviewed": True,
                      "source_cells": {k: "'Synthetic'!A1" for k in
                                       ("character", "equipment", "pose", "location", "lighting")},
                      "lighting_radius_m": None, "lighting_radius_status": "unknown",
                      "approved_prompt_sha256": h(self.prompt),
                      "ordered_reference_cells": [x["cell"] for x in self.images],
                      "reference_sha256": {x["cell"]: x["sha256"] for x in self.images},
                      "required_positive_phrases": ["white puppet", "golden eyes", "right hand bronze spear"]}
        self.save()

    def save(self):
        (self.folder / "artist_scene1_manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        (self.folder / "artist_guard_attestation.json").write_text(json.dumps(self.proof), encoding="utf-8")

    def check(self):
        return verify_package(self.folder)

    def test_original_locked_package_passes(self):
        m, prompt, originals = self.check()
        self.assertEqual(m["scene_id"], "TEST-SCENE")
        self.assertEqual(prompt.encode("utf-8"), self.prompt)
        self.assertEqual(len(originals), 2)

    def test_mutated_prompt_rejected(self):
        (self.folder / "positive.txt").write_bytes(self.prompt + b" changed")
        with self.assertRaises(Reject): self.check()

    def test_manifest_hash_change_rejected(self):
        self.manifest["prompt_sha256"] = h(b"other")
        self.save()
        with self.assertRaises(Reject): self.check()

    def test_reference_bytes_tamper_rejected(self):
        (self.folder / "reference_D91.png").write_bytes(self.png + b"changed")
        with self.assertRaises(Reject): self.check()

    def test_reference_order_swap_rejected(self):
        self.manifest["references"] = list(reversed(self.images))
        self.save()
        with self.assertRaises(Reject): self.check()

    def test_reference_role_missing_rejected(self):
        self.manifest["references"][0]["role"] = "costume"
        self.save()
        with self.assertRaises(Reject): self.check()

    def test_hud_in_positive_prompt_rejected_even_if_rehashed(self):
        bad = self.prompt + b" HUD"
        (self.folder / "positive.txt").write_bytes(bad)
        self.manifest["prompt_sha256"] = h(bad)
        self.proof["approved_prompt_sha256"] = h(bad)
        self.save()
        with self.assertRaises(Reject): self.check()

    def test_missing_private_attestation_rejected(self):
        (self.folder / "artist_guard_attestation.json").unlink()
        with self.assertRaises(Reject): self.check()

    def test_source_unreviewed_rejected(self):
        self.proof["reviewed_live_sources"] = False
        self.save()
        with self.assertRaises(Reject): self.check()

    def test_pixels_unreviewed_rejected(self):
        self.proof["pixels_reviewed"] = False
        self.save()
        with self.assertRaises(Reject): self.check()

    def test_missing_source_cell_rejected(self):
        del self.proof["source_cells"]["lighting"]
        self.save()
        with self.assertRaises(Reject): self.check()

    def test_unknown_light_allowed_without_invention(self):
        self.proof["lighting_radius_m"] = None
        self.proof["lighting_radius_status"] = "unknown"
        self.save()
        self.assertEqual(len(self.check()[2]), 2)

    def test_fabricated_radius_marker_rejected(self):
        self.proof["lighting_radius_m"] = None
        self.proof["lighting_radius_status"] = "confirmed"
        self.save()
        with self.assertRaises(Reject): self.check()

    def test_explicit_confirmed_light_radius_allowed(self):
        self.proof["lighting_radius_m"] = 2
        self.proof["lighting_radius_status"] = "confirmed"
        self.save()
        self.assertEqual(len(self.check()[2]), 2)

    def test_unchecked_scene_phrase_rejected(self):
        self.proof["required_positive_phrases"].append("lit lantern")
        self.save()
        with self.assertRaises(Reject): self.check()

    def test_path_traversal_rejected(self):
        self.manifest["prompt_file"] = "../positive.txt"
        self.save()
        with self.assertRaises(Reject): self.check()

    def test_wrong_queue_rejected(self):
        self.manifest["queue_row"] = 5
        self.save()
        with self.assertRaises(Reject): self.check()

    def test_missing_png_rejected(self):
        (self.folder / "reference_D91.png").unlink()
        with self.assertRaises(Reject): self.check()


if __name__ == "__main__":
    unittest.main()
