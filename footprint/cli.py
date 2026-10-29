"""Command line entry point.

    python -m footprint scan --family data/synthetic/families/fam-001.json
    python -m footprint scan-all
    python -m footprint scan-all --llm gemini --lang ar
    python -m footprint scan-all --llm ollama
"""
import argparse
import logging
import pathlib

from .consent import PrivacyGuard
from .detectors import run_all
from .explain import explain
from .linker import build_context
from .loader import load_family, load_world
from .playbook import actions_for


def scan(family_path, world, out, llm, lang, strict):
    family = load_family(family_path)
    ctx = build_context(family, world)
    findings = PrivacyGuard(ctx, strict=strict).filter(run_all(ctx))
    for f in findings:
        f.actions = f.actions or actions_for(f.category)
        f.explanation = explain(f, ctx, backend=llm, lang=lang)
    from .report import write
    write(ctx, findings, out)
    print(f"{family['family_id']}: {len(findings)} finding(s) -> {out}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="footprint")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("scan", "scan-all"):
        p = sub.add_parser(name)
        if name == "scan":
            p.add_argument("--family", required=True)
        else:
            p.add_argument("--families", default="data/synthetic/families")
        p.add_argument("--world", action="append", default=None,
                       help="world directory (repeatable); default data/synthetic/world")
        p.add_argument("--out", default="out")
        p.add_argument("--llm", default="template", choices=["template", "gemini", "ollama", "openai"])
        p.add_argument("--lang", default="en", choices=["en", "ar"])
        p.add_argument("--strict", action="store_true", help="raise instead of dropping unsafe findings")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    world = load_world(*(a.world or ["data/synthetic/world"]))
    paths = [a.family] if a.cmd == "scan" else sorted(pathlib.Path(a.families).glob("*.json"))
    for path in paths:
        scan(path, world, a.out, a.llm, a.lang, a.strict)
    return 0
