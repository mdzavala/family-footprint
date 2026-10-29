"""Baseline detectors. They work, but they are deliberately simple. Improve them!

Known gaps (each one costs points on the leaderboard):
- home_location only looks at photo GPS, not people-search addresses.
- account_linkage always says 'low', even when the account belongs to a minor.
"""
from ..linker import norm_phone
from ..models import Finding

SENSITIVE = {"phone", "date_of_birth", "address"}


def credential_leak(ctx):
    out = []
    for mid, ml in ctx.links.items():
        hits = [b for b in ml.breaches if b.get("password_exposed")]
        if hits:
            names = ", ".join(sorted({b["breach"] for b in hits}))
            out.append(Finding("CREDENTIAL_LEAK", mid, "high", [b["id"] for b in hits],
                               summary=f"Password exposed in {len(hits)} breach(es): {names}"))
    return out


def personal_data_leak(ctx):
    out = []
    for mid, ml in ctx.links.items():
        hits = [b for b in ml.breaches
                if not b.get("password_exposed") and SENSITIVE & set(b["data_classes"])]
        if hits:
            classes = sorted(set().union(*(SENSITIVE & set(b["data_classes"]) for b in hits)))
            out.append(Finding("PERSONAL_DATA_LEAK", mid, "medium", [b["id"] for b in hits],
                               summary=f"Breach exposed: {', '.join(classes)}"))
    return out


def contact_exposed(ctx):
    out = []
    for mid, ml in ctx.links.items():
        ids = [i for i in ml.member["identifiers"] if i.get("verified")]
        phones = {norm_phone(i["value"]) for i in ids if i["type"] == "phone"}
        emails = {i["value"].lower() for i in ids if i["type"] == "email"}
        evidence = [bk["id"] for bk in ml.brokers]
        for p in ml.profiles:
            bio = p.get("bio", "")
            if any(ph and ph in norm_phone(bio) for ph in phones) or any(e in bio.lower() for e in emails):
                evidence.append(p["id"])
        if evidence:
            out.append(Finding("CONTACT_EXPOSED", mid, "medium", evidence,
                               summary="Phone or email is publicly listed"))
    return out


def home_location(ctx):
    out = []
    for mid, ml in ctx.links.items():
        geo = [ph for ph in ml.photos if ph.get("exif", {}).get("gps_lat") is not None]
        if geo:
            evidence = [ph["id"] for ph in geo] + [ph["post_id"] for ph in geo]
            out.append(Finding("HOME_LOCATION", mid, "high", evidence,
                               summary="Public photo carries precise GPS coordinates"))
        # TODO(challenge): people-search listings with an address_place_id also reveal home.
    return out


def account_linkage(ctx):
    out = []
    for mid, ml in ctx.links.items():
        by_name = {}
        for p in ml.profiles:
            by_name.setdefault(p["username"].lower(), []).append(p)
        for username, profiles in by_name.items():
            if len({p["platform"] for p in profiles}) >= 2:
                out.append(Finding("ACCOUNT_LINKAGE", mid, "low", [p["id"] for p in profiles],
                                   summary=f"Username '{username}' links accounts on "
                                           f"{', '.join(sorted({p['platform'] for p in profiles}))}"))
                break  # one finding per member
        # TODO(challenge): a minor's accounts being linkable deserves a higher severity.
    return out
