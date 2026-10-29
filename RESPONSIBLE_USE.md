# Responsible use

Family Footprint exists to help people protect **themselves and the family members who have agreed to be included**. An OSINT tool pointed at the wrong person becomes a stalking tool, so these rules are part of the product, not an add-on.

## What this tool is for
- A family looking at its own public exposure, with everyone's agreement
- Reducing scam, fraud and safety risk: leaked passwords, located homes, predictable routines, cloned voices

## What it must never do
- **Look up someone else.** No search by name, photo or address. A scan only starts from identifiers (email, phone, username) that the person has **proved they own** with a one-time code.
- **Include anyone who hasn't agreed.** Adults accept their own invite. Children are added by a verified guardian. If consent is pending or declined, that person is not scanned and not mentioned in findings.
- **Keep what it doesn't need.** Process locally, store as little as possible, delete raw collected data after the report.
- **Send real family data to third-party AI services.** At the hackathon the data is synthetic, so Gemma through the Gemini API is fine. A real-world version must run the model on-device or self-hosted.

## Built-in safeguards in this repo
| Safeguard | Where |
|---|---|
| Only consented members are scanned | `footprint/consent.py`: `eligible_members` |
| Only verified identifiers are used | `footprint/consent.py`: `verified_identifiers` |
| Names never used as search keys | `footprint/linker.py` matches on email, phone and username only |
| Findings citing unlinked records are dropped | `footprint/consent.py`: `PrivacyGuard` |
| LLM prompts exclude emails, phones, usernames | `footprint/explain.py` |
| Decoys + penalties keep everyone honest | `eval/score.py`, `tests/test_privacy.py` |

## Data in this repository
All data is **synthetic**. Every person, email, phone number, company, school, breach and place is invented. Do not add real personal data to this repository, your fork, your demo or your slides.

## If you build on this after the hackathon
Real-world sources (breach-notification services, social platforms, people-search sites) come with their own terms of service and with data-protection and cybercrime laws, including in the UAE. Check those terms and laws, and get proper legal advice, before connecting any real source.

## Reporting misuse or a safety issue
Open an issue marked `safety` or contact the maintainers privately. Don't publish details of an exploit or misuse path before it's fixed.
