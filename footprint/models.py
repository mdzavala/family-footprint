from dataclasses import dataclass, field, asdict

CATEGORIES = [
    "CREDENTIAL_LEAK",       # a verified email/phone appears in a breach that exposed passwords
    "PERSONAL_DATA_LEAK",    # a breach exposed phone, date of birth or address (no password)
    "CONTACT_EXPOSED",       # phone/email publicly listed (people-search site, public bio)
    "HOME_LOCATION",         # home can be located (photo GPS, people-search address)
    "ACCOUNT_LINKAGE",       # same username ties accounts together across platforms
    "CHILD_IDENTIFIABLE",    # a child's full name + school can be pieced together publicly
    "ROUTINE_PATTERN",       # a predictable schedule: same place, same weekday, same time
    "VOICE_CLONE_RISK",      # long public recordings of someone's voice
    "IMPERSONATION_TARGET",  # public senior/finance role + family details = scam target
]
SEVERITIES = ["low", "medium", "high", "critical"]


@dataclass
class Finding:
    category: str
    member_id: str
    severity: str
    evidence: list
    summary: str = ""
    explanation: str = ""
    actions: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)
