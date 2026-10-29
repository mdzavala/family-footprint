"""Consent and privacy guardrails. Do not weaken these: the scorer penalises violations.

Rules
1. Only members with consent status 'verified' (adults) or 'guardian_verified' (minors,
   whose guardian is themselves verified) can be scanned.
2. Only identifiers marked verified (proved by one-time code) are used to search.
3. Names are NEVER used to search the world. They may only be used to read content
   that was already linked through a verified identifier (e.g. a parent's own post).
4. Every finding's evidence must be reachable through rule 2.
"""
import logging

log = logging.getLogger("footprint.privacy")


class PrivacyViolation(Exception):
    pass


def eligible_members(family):
    members = {m["member_id"]: m for m in family["members"]}
    out = []
    for m in family["members"]:
        status = m.get("consent", {}).get("status")
        if status == "verified":
            out.append(m)
        elif status == "guardian_verified":
            guardian = members.get(m["consent"].get("guardian_id"))
            if guardian and guardian.get("consent", {}).get("status") == "verified" \
                    and guardian.get("role") == "guardian":
                out.append(m)
    return out


def verified_identifiers(member):
    return [i for i in member.get("identifiers", []) if i.get("verified") is True]


class PrivacyGuard:
    """Last line of defence: drops (or, in strict mode, raises on) unsafe findings."""

    def __init__(self, ctx, strict=False):
        self.allowed_members = {m["member_id"] for m in ctx.members}
        self.allowed_evidence = ctx.linked_ids
        self.strict = strict

    def filter(self, findings):
        safe = []
        for f in findings:
            problem = None
            if f.member_id not in self.allowed_members:
                problem = f"member {f.member_id} has not consented"
            else:
                bad = [e for e in f.evidence if e not in self.allowed_evidence]
                if bad:
                    problem = f"evidence {bad} is not linked to a verified identifier"
            if problem:
                if self.strict:
                    raise PrivacyViolation(f"{f.category}: {problem}")
                log.warning("Dropped %s finding: %s", f.category, problem)
                continue
            safe.append(f)
        return safe
