"""Write the findings JSON (scored by eval/score.py) and a readable Markdown report."""
import json
import pathlib

ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
ROLE = {"guardian": "Parent", "adult": "Adult", "child": "Child", "elder": "Grandparent"}


def write(ctx, findings, out_dir):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    fid = ctx.family["family_id"]
    payload = {"family_id": fid, "findings": [f.to_dict() for f in findings]}
    (out / f"{fid}.findings.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [f"# Family Footprint report: {ctx.family.get('label', fid)}", "",
             f"Scanned {len(ctx.members)} consented member(s). "
             f"{len(findings)} exposure(s) found.", ""]
    skipped = [m for m in ctx.family["members"] if m not in ctx.members]
    if skipped:
        lines += [f"Not scanned (no consent yet): {len(skipped)} member(s).", ""]
    top = sorted(findings, key=lambda f: ORDER.get(f.severity, 9))[:5]
    if top:
        lines += ["## Fix these first", ""]
        for n, f in enumerate(top, 1):
            m = ctx.member(f.member_id)
            lines.append(f"{n}. **{f.actions[0] if f.actions else f.category}** "
                         f"({ROLE.get(m['role'], m['role'])} {m['names']['first']}, {f.severity})")
        lines.append("")
    for m in ctx.members:
        mine = sorted([f for f in findings if f.member_id == m["member_id"]],
                      key=lambda f: ORDER.get(f.severity, 9))
        lines += [f"## {ROLE.get(m['role'], m['role'])}: {m['names']['first']}", ""]
        if not mine:
            lines += ["No exposures found.", ""]
        for f in mine:
            lines += [f"### {f.category.replace('_', ' ').title()} ({f.severity})", "",
                      f.explanation or f.summary, ""]
            lines += [f"- {a}" for a in f.actions] + ["", f"<sub>Evidence: {', '.join(f.evidence)}</sub>", ""]
    (out / f"{fid}.report.md").write_text("\n".join(lines), encoding="utf-8")
