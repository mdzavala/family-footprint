"""Plain-language fix actions per category, written for non-technical parents."""

PLAYBOOK = {
    "CREDENTIAL_LEAK": [
        "Change the password on the breached site and anywhere you reused it.",
        "Turn on two-step verification (an app code, not SMS where possible) for email first.",
        "Start using a password manager so every account gets a unique password.",
    ],
    "PERSONAL_DATA_LEAK": [
        "Expect convincing scam calls or messages that quote your date of birth or address.",
        "Agree as a family: no one shares codes or confirms details on inbound calls.",
        "Ask your bank and telecom provider to add a PIN or passphrase to your account.",
    ],
    "CONTACT_EXPOSED": [
        "Request removal from people-search sites that list you.",
        "Use a separate business number or contact form instead of a personal number in public bios.",
        "Turn on spam and unknown-caller filtering on your phone.",
    ],
    "HOME_LOCATION": [
        "Turn off location tagging for the camera app on every family phone.",
        "Delete or re-upload past photos taken at home without location data.",
        "Request removal of your address from people-search sites.",
    ],
    "ACCOUNT_LINKAGE": [
        "Use different usernames for anonymous or gaming accounts and real-name accounts.",
        "Review what the linked accounts reveal together, not just one by one.",
        "For teenagers: talk about it together rather than banning the account.",
    ],
    "CHILD_IDENTIFIABLE": [
        "Avoid posting a child's full name together with their school or uniform.",
        "Make family photo accounts private and review who follows them.",
        "Ask grandparents and relatives to follow the same rule.",
    ],
    "ROUTINE_PATTERN": [
        "Post about activities after they happen, not while you are there.",
        "Avoid tagging the same place on the same day every week.",
        "Agree on a pick-up rule: children only leave with a pre-agreed adult.",
    ],
    "VOICE_CLONE_RISK": [
        "Set up a family safe word for any urgent call asking for money or codes.",
        "If a 'family member' calls in distress, hang up and call them back on their known number.",
        "Brief older relatives: a familiar voice is no longer proof of identity.",
    ],
    "IMPERSONATION_TARGET": [
        "Tell your finance team: no payment changes approved by voice note, WhatsApp or email alone.",
        "Use a call-back rule on a known number for any urgent or unusual request.",
        "Avoid announcing travel dates publicly while you are away.",
    ],
}


def actions_for(category):
    return list(PLAYBOOK.get(category, []))
