"""Challenge detectors. These are the hard, human-impact risks. Build them!

Each function receives a Context (see linker.py):
    ctx.members              consented members only
    ctx.links[member_id]     MemberLinks: breaches, profiles, posts, photos, brokers
    ctx.family_posts()       [(author_member_id, post)] across the whole family
    ctx.world["index"][id]   look up any record by id (e.g. a post's place_id)

Rules (see RESPONSIBLE_USE.md and consent.py):
    - Never search the world by name. You MAY match a member's declared first name
      inside posts that are already linked (e.g. a parent's post about their child).
    - Evidence must only cite records already linked to the family.

Return a list of models.Finding(category, member_id, severity, evidence, summary=...).
Your open-source LLM can help: classify posts, extract schools, spot routines.
"""


def child_identifiable(ctx):
    """CHILD_IDENTIFIABLE: a child's full name + school can be pieced together publicly.

    Hint: for members with role 'child', scan ctx.family_posts() for their first AND last
    name, then check whether the post (or its place_id) points to a place of kind 'school'.
    Suggested severity: high.
    """
    return []


def routine_pattern(ctx):
    """ROUTINE_PATTERN: same place, same weekday, similar hour, repeated (2+ times).

    Hint: group linked posts by (place_id, weekday, hour). Attribute the finding to the
    person whose routine is exposed (if a parent posts 'swim club with <child>',
    that's the child's routine). Children's routines are higher risk.
    Suggested severity: high.
    """
    return []


def voice_clone_risk(ctx):
    """VOICE_CLONE_RISK: long public recordings of an adult's voice.

    Hint: posts with media == 'video' and has_voice == True on a member's own accounts.
    A few seconds of clean audio is enough for today's voice-cloning tools.
    Suggested severity: medium.
    """
    return []


def impersonation_target(ctx):
    """IMPERSONATION_TARGET: a public senior/finance role + public family details.

    This is the CEO-fraud / 'family emergency' scam pattern: an attacker knows who signs
    off payments AND when the family is away. Hint: look for executive/finance keywords in
    a member's public profile bio, combined with family posts that mention the member or
    reveal travel plans. Evidence should cite both.
    Suggested severity: high.
    """
    return []
