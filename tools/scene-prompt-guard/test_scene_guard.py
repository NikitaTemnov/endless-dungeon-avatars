import copy
import unittest
from scene_guard import Reject, positive_prompt, artist_handoff

BASE = {
  "category":"scene", "race_profile":"adult_biosynthetic_skitalets",
  "style_profile":"cinematic_aaa_dark_fantasy_pbr",
  "generator_prompt_is_controllable":True,
  "scene_id":"TEST-001", "hero":"Test Skitalets",
  "final_moment":"Standing beside the central column",
  "sources":{"character":"Persona!C3","equipment":"Equip!A4","pose":"Notes!C48",
             "location":"Locations!D78","lighting":"Lighting!B8"},
  "references":{"pixels_reviewed":True,
                "morphology":["https://example.org/morphology.png"],
                "environment":["https://example.org/environment.png"]},
  "character":{"body":"Adult normal proportions","face":"Sculpted pale face","eyes":"Purple"},
  "equipment":["Blue fabric overalls", "Black boots"],
  "pose":{"stance":"Standing beside stone column","right_hand":"Steel knife lowered",
          "left_hand":"Free bare hand"},
  "location":{"name":"Dry stone chamber","near_geometry":"three natural niches",
              "far_geometry":"unexplored opening in darkness"},
  "lighting":{"source":"small violet projection","useful_radius_m":2,"background":"dark"},
  "visible_props":[{"description":"central stone column","source":"Locations!D78",
                    "distance_m":0.8}]
}

class GuardTest(unittest.TestCase):
    def test_accepts(self):
        p=positive_prompt(BASE)
        self.assertIn("adult, artificial biosynthetic Skitalets",p)
    def test_ui_and_bad_style_rejected(self):
        for term in ("Russian narrative panels", "game interface", "HUD",
                     "chibi", "helmet", "tactical gear", "шлем"):
            with self.subTest(term=term):
                s=copy.deepcopy(BASE)
                s["final_moment"]+=" "+term
                with self.assertRaises(Reject): positive_prompt(s)
    def test_unknown_payload_blocks(self):
        s=copy.deepcopy(BASE)
        s["generator_prompt_is_controllable"]=False
        with self.assertRaises(Reject): positive_prompt(s)
        self.assertIn("Художник",artist_handoff(s,3,"hidden generator prompt"))
    def test_missing_originals_blocks(self):
        s=copy.deepcopy(BASE)
        s["references"]["pixels_reviewed"]=False
        with self.assertRaises(Reject): positive_prompt(s)
    def test_light_distance_blocks(self):
        s=copy.deepcopy(BASE)
        s["visible_props"][0]["distance_m"]=12
        with self.assertRaises(Reject): positive_prompt(s)
    def test_escalation_requires_three(self):
        with self.assertRaises(Reject): artist_handoff(BASE,2,"bad pixels")

if __name__=="__main__":
    unittest.main()
