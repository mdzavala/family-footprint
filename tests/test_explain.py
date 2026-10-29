"""Explanation backends: data minimisation and graceful fallback."""
import os
import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from footprint import explain as ex  # noqa: E402
from footprint.detectors import run_all  # noqa: E402
from footprint.linker import build_context  # noqa: E402
from footprint.loader import load_family, load_world  # noqa: E402

CTX = build_context(load_family(ROOT / "data/synthetic/families/fam-001.json"),
                    load_world(ROOT / "data/synthetic/world"))
FINDING = run_all(CTX)[0]


class ExplainTests(unittest.TestCase):
    def test_prompt_never_contains_identifiers(self):
        captured = {}

        def fake_post(url, payload, headers=None):
            captured["body"] = str(payload)
            return {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}

        with mock.patch.object(ex, "_post", fake_post), mock.patch.dict(os.environ, {"GEMINI_API_KEY": "x"}):
            self.assertEqual(ex.explain(FINDING, CTX, backend="gemini"), "ok")
        for m in CTX.members:
            for i in m["identifiers"]:
                self.assertNotIn(i["value"], captured["body"])

    def test_missing_key_falls_back_to_template(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            out = ex.explain(FINDING, CTX, backend="gemini")
        self.assertIn("model unavailable", out)


if __name__ == "__main__":
    unittest.main()
