"""Link world records to consented family members, using verified identifiers only."""
import re
from dataclasses import dataclass, field

from .consent import eligible_members, verified_identifiers


def norm_phone(s):
    return re.sub(r"\D", "", s or "")


@dataclass
class MemberLinks:
    member: dict
    breaches: list = field(default_factory=list)
    profiles: list = field(default_factory=list)
    posts: list = field(default_factory=list)
    photos: list = field(default_factory=list)
    brokers: list = field(default_factory=list)


@dataclass
class Context:
    family: dict
    world: dict
    members: list
    links: dict            # member_id -> MemberLinks
    linked_ids: set        # every world id reachable via verified identifiers (+ places)

    def member(self, member_id):
        return self.links[member_id].member

    def family_posts(self):
        """All posts from any consented member's linked accounts: (author_member_id, post)."""
        return [(mid, p) for mid, ml in self.links.items() for p in ml.posts]


def build_context(family, world):
    members = eligible_members(family)
    links, linked = {}, set()
    for m in members:
        ml = MemberLinks(member=m)
        ids = verified_identifiers(m)
        emails = {i["value"].lower() for i in ids if i["type"] == "email"}
        phones = {norm_phone(i["value"]) for i in ids if i["type"] == "phone"}
        usernames = {i["value"].lower() for i in ids if i["type"] == "username"}

        for b in world["breaches"]:
            v = b["identifier"]
            if (b["identifier_type"] == "email" and v.lower() in emails) or \
               (b["identifier_type"] == "phone" and norm_phone(v) in phones):
                ml.breaches.append(b)

        for p in world["profiles"]:
            by_email = (p.get("linked_email") or "").lower() in emails
            by_phone = bool(p.get("linked_phone")) and norm_phone(p["linked_phone"]) in phones
            by_username = p["username"].lower() in usernames
            if by_email or by_phone or by_username:
                ml.profiles.append(p)

        profile_ids = {p["id"] for p in ml.profiles}
        ml.posts = [p for p in world["posts"] if p["profile_id"] in profile_ids]
        post_ids = {p["id"] for p in ml.posts}
        ml.photos = [ph for ph in world["photos"] if ph["post_id"] in post_ids]

        for bk in world["brokers"]:
            if (bk.get("email") or "").lower() in emails or \
               (bk.get("phone") and norm_phone(bk["phone"]) in phones):
                ml.brokers.append(bk)

        for group in (ml.breaches, ml.profiles, ml.posts, ml.photos, ml.brokers):
            linked.update(r["id"] for r in group)
        links[m["member_id"]] = ml

    linked.update(pl["id"] for pl in world["places"])  # places are public reference data
    return Context(family=family, world=world, members=members, links=links, linked_ids=linked)
