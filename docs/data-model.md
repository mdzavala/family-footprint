# Data model

## Family file (`data/synthetic/families/*.json`)
```json
{
  "family_id": "fam-001",
  "members": [{
    "member_id": "fam-001-m1",
    "role": "guardian | adult | child | elder",
    "age_band": "40-49",
    "names": {"first": "Layla", "last": "Haddad"},
    "consent": {"status": "verified | guardian_verified | pending | declined", "guardian_id": "..."},
    "identifiers": [{"type": "email | phone | username", "value": "...", "verified": true}]
  }]
}
```
`names` are declared by the family. They may only be used to read content **already linked** through a verified identifier, never to search.

## World (`data/synthetic/world/*.json`)
Every `*.json` file in a world directory is merged, which is how the hidden family is added at judging time.

| List | Key fields | Links to a member by |
|---|---|---|
| `breaches` | `breach`, `identifier_type`, `identifier`, `data_classes`, `password_exposed` | email / phone |
| `profiles` | `platform`, `username`, `display_name`, `linked_email`, `bio`, `visibility` | linked_email / username |
| `posts` | `profile_id`, `posted_at` (ISO, +04:00), `text`, `place_id`, `media`, `has_voice`, `photo_id` | via profile |
| `photos` | `post_id`, `exif.gps_lat`, `exif.gps_lon`, `exif.taken_at` | via post |
| `brokers` | people-search listing: `name`, `phone`, `email`, `address_place_id`, `relatives` | email / phone |
| `places` | `name`, `kind` (home, school, club, work), `lat`, `lon` | reference data |

## Findings output (`out/<family_id>.findings.json`)
This is what the scorer reads. Keep the format.
```json
{
  "family_id": "fam-001",
  "findings": [{
    "category": "CHILD_IDENTIFIABLE",
    "member_id": "fam-001-m3",
    "severity": "low | medium | high | critical",
    "evidence": ["PO-101"],
    "summary": "short machine summary",
    "explanation": "2 calm sentences for a parent",
    "actions": ["..."]
  }]
}
```
- One finding per `(category, member_id)`. Extra duplicates are ignored, not rewarded.
- `member_id` is the person **whose** risk it is. If a parent posts "swim club with Yasmin every Tuesday", the routine belongs to Yasmin.
- `evidence` must only cite records linked to the family. Citing a decoy is a privacy violation.
