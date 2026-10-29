"""Score findings against answer keys.

    python eval/score.py                       # scores out/ against eval/answer_keys/
    python eval/score.py --pred out --keys eval/answer_keys --json

Per family (0-100):
    detection   up to 80 pts  weighted recall: each expected finding is worth its severity
                              (low=1, medium=2, high=3, critical=4), matched on (category, member)
    severity    up to 20 pts  share of your correct detections that carry the right severity
    noise       -5 per false positive (a finding that is not in the answer key)
    privacy     -10 per violation: a finding about a member who did not consent, or evidence
                citing a record that belongs to someone else
Final score = average over families. Privacy violations can push a family to 0.
"""
import argparse
import json
import pathlib
import sys


def score_family(key, pred):
    expected = key["expected"]
    preds = pred.get("findings", []) if pred else []
    forbidden_members = set(key.get("forbidden_members", []))
    forbidden_evidence = set(key.get("forbidden_evidence", []))

    violations = []
    clean = []
    for f in preds:
        bad_ev = sorted(set(f.get("evidence", [])) & forbidden_evidence)
        if f.get("member_id") in forbidden_members:
            violations.append(f"{f.get('category')}: member {f.get('member_id')} did not consent")
        elif bad_ev:
            violations.append(f"{f.get('category')}: evidence {bad_ev} belongs to someone else")
        else:
            clean.append(f)

    matched, sev_ok, used = [], 0, set()
    for exp in expected:
        ok_members = {exp["member_id"], *exp.get("accept_members", [])}
        for i, f in enumerate(clean):
            if i not in used and f.get("category") == exp["category"] and f.get("member_id") in ok_members:
                used.add(i)
                matched.append(exp["category"] + "/" + exp["member_id"])
                sev_ok += f.get("severity") == exp["severity"]
                break
    tp = len(matched)
    # duplicates of an already matched pair are not penalised as false positives
    seen_pairs = {(clean[i].get("category"), clean[i].get("member_id")) for i in used}
    fp = sum(1 for i, f in enumerate(clean)
             if i not in used and (f.get("category"), f.get("member_id")) not in seen_pairs)
    fn = len(expected) - tp
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    weight = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    total_w = sum(weight[e["severity"]] for e in expected)
    got_w = sum(weight[e["severity"]] for e in expected if e["category"] + "/" + e["member_id"] in matched)
    w_recall = got_w / total_w if total_w else 0.0
    sev = sev_ok / tp if tp else 0.0
    score = max(0.0, 80 * w_recall + 20 * sev - 5 * fp - 10 * len(violations))
    missed = [e["category"] + "/" + e["member_id"] for e in expected
              if e["category"] + "/" + e["member_id"] not in matched]
    return {"family_id": key["family_id"], "score": round(score, 1), "precision": round(precision, 3),
            "recall": round(recall, 3), "weighted_recall": round(w_recall, 3), "severity_accuracy": round(sev, 3), "false_positives": fp,
            "privacy_violations": violations, "missed": missed}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", default="out")
    ap.add_argument("--keys", action="append", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    keys = []
    for d in a.keys or ["eval/answer_keys"]:
        keys += sorted(pathlib.Path(d).glob("*.json"))
    if not keys:
        print("No answer keys found.", file=sys.stderr)
        return 1
    results = []
    for kp in keys:
        key = json.loads(kp.read_text(encoding="utf-8"))
        pp = pathlib.Path(a.pred) / f"{key['family_id']}.findings.json"
        pred = json.loads(pp.read_text(encoding="utf-8")) if pp.exists() else None
        results.append(score_family(key, pred))
    total = round(sum(r["score"] for r in results) / len(results), 1)
    if a.json:
        print(json.dumps({"total": total, "families": results}, indent=2))
        return 0
    for r in results:
        print(f"{r['family_id']}: {r['score']:5.1f}  P={r['precision']:.2f} R={r['recall']:.2f} "
              f"weighted_R={r['weighted_recall']:.2f} severity={r['severity_accuracy']:.2f} FP={r['false_positives']}")
        for v in r["privacy_violations"]:
            print(f"   PRIVACY VIOLATION  {v}")
        for m in r["missed"]:
            print(f"   missed             {m}")
    print(f"\nTOTAL: {total} / 100")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
