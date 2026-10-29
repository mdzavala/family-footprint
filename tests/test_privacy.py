"""Privacy guardrail tests. Run: python -m unittest discover tests

These must keep passing whatever you change. Judges will run them.
"""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

from footprint.consent import PrivacyGuard, PrivacyViolation, eligible_members  # noqa: E402
from footprint.detectors import run_all  # noqa: E402
from footprint.linker import build_context  # noqa: E402
from footprint.loader import load_family, load_world  # noqa: E402
from footprint.models import Finding  # noqa: E402
from score import score_family  # noqa: E402

WORLD = load_world(ROOT / "data/synthetic/world")
FAM1 = load_family(ROOT / "data/synthetic/families/fam-001.json")


class ConsentTests(unittest.TestCase):
    def test_pending_member_is_not_scanned(self):
        ids = {m["member_id"] for m in eligible_members(FAM1)}
        self.assertNotIn("fam-001-m4", ids)

    def test_child_needs_verified_guardian(self):
        fam = load_family(ROOT / "data/synthetic/families/fam-001.json")
        fam["members"][0]["consent"]["status"] = "pending"   # guardian not verified
        ids = {m["member_id"] for m in eligible_members(fam)}
        self.assertNotIn("fam-001-m3", ids)

    def test_unverified_identifiers_are_not_linked(self):
        ctx = build_context(FAM1, WORLD)
        self.assertNotIn("BR-103", ctx.linked_ids)   # Samir's breach (pending consent)
        self.assertNotIn("BR-104", ctx.linked_ids)   # a different Layla Haddad
        self.assertNotIn("BK-102", ctx.linked_ids)   # same name, different person


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.ctx = build_context(FAM1, WORLD)

    def test_guard_drops_non_consented_member(self):
        bad = Finding("CREDENTIAL_LEAK", "fam-001-m4", "high", ["BR-103"])
        self.assertEqual(PrivacyGuard(self.ctx).filter([bad]), [])

    def test_guard_drops_unlinked_evidence(self):
        bad = Finding("CONTACT_EXPOSED", "fam-001-m1", "medium", ["BK-102"])
        self.assertEqual(PrivacyGuard(self.ctx).filter([bad]), [])

    def test_strict_mode_raises(self):
        bad = Finding("CONTACT_EXPOSED", "fam-001-m1", "medium", ["BK-102"])
        with self.assertRaises(PrivacyViolation):
            PrivacyGuard(self.ctx, strict=True).filter([bad])

    def test_detectors_never_need_the_guard(self):
        """Your detectors should be clean on their own: strict mode must not raise."""
        for fam_path in sorted((ROOT / "data/synthetic/families").glob("*.json")):
            ctx = build_context(load_family(fam_path), WORLD)
            PrivacyGuard(ctx, strict=True).filter(run_all(ctx))


class ScorerTests(unittest.TestCase):
    def test_violation_is_penalised(self):
        key = {"family_id": "x", "expected": [], "forbidden_members": ["m4"], "forbidden_evidence": []}
        pred = {"findings": [{"category": "CREDENTIAL_LEAK", "member_id": "m4", "severity": "high", "evidence": []}]}
        self.assertEqual(len(score_family(key, pred)["privacy_violations"]), 1)


if __name__ == "__main__":
    unittest.main()
