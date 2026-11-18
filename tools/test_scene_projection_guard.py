"""Regression tests for ED-SYMBIOT-IDENTITY-HOLOGRAM-GATE-20261118."""
from copy import deepcopy
import unittest
from scene_projection_guard import KIND, positive_fragment, validate

class TestProjectionPreflight(unittest.TestCase):
    def setUp(self):
        self.scene = {
            "scene_id": "ED-SKAL-022",
            "hero": "Скалоглав",
            "symbiote": {"name": "Бурундук", "anchor": "FOREHEAD_CRYSTAL"},
            "projection": {
                "active": True, "kind": KIND, "shape": "GEOMETRIC_PANEL",
                "color": "green", "distance_m": 0.25, "light_radius_m": 1.5,
            },
            "visual_description": "Зелёное энергетическое информационное окно системы у лобного кристалла",
        }

    def test_valid_info_window(self):
        self.assertEqual(validate(self.scene), [])
        fragment = positive_fragment(self.scene)
        self.assertIn("GEOMETRIC ENERGY INFORMATION WINDOW", fragment)
        self.assertNotIn("Бурундук", fragment)

    def test_literal_animal_projection_blocked(self):
        scene = deepcopy(self.scene)
        scene["visual_description"] = "маленькая полупрозрачная зелёная проекция Бурундука"
        self.assertTrue(validate(scene))
        with self.assertRaises(ValueError):
            positive_fragment(scene)

    def test_squirrel_blocked(self):
        scene = deepcopy(self.scene)
        scene["visual_description"] = "зелёная белка вместо интерфейса"
        self.assertTrue(validate(scene))

    def test_wrong_kind_blocked(self):
        scene = deepcopy(self.scene)
        scene["projection"]["kind"] = "ANIMAL_AVATAR"
        self.assertTrue(validate(scene))

    def test_window_outside_half_meter_blocked(self):
        scene = deepcopy(self.scene)
        scene["projection"]["distance_m"] = 0.75
        self.assertTrue(validate(scene))

    def test_forehead_color_and_light_enforced(self):
        scene = deepcopy(self.scene)
        scene["projection"]["color"] = "blue"
        scene["projection"]["light_radius_m"] = 7
        self.assertGreaterEqual(len(validate(scene)), 2)

    def test_closed_projection_adds_nothing(self):
        scene = deepcopy(self.scene)
        scene["projection"] = {"active": False}
        self.assertEqual(validate(scene), [])
        self.assertEqual(positive_fragment(scene), "")

    def test_other_hero_does_not_inherit_skal_color(self):
        scene = deepcopy(self.scene)
        scene["hero"] = "Ник"
        scene["symbiote"] = {"name": "Чёрный Чешир", "anchor": "CHEST_CRYSTAL"}
        scene["projection"]["color"] = "blue"
        self.assertEqual(validate(scene), [])

if __name__ == "__main__":
    unittest.main()
