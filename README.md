# Family Footprint

**See what the internet knows about your family, before a scammer does.**

An open-source, privacy-first OSINT challenge built on open AI models.
*Challenge by [CysuiteONE](https://cysuiteone.com).*

---

## The problem

Scammers no longer need to hack anyone. They read.

A parent's proud post gives away a child's full name and school. A weekly "swim club!" photo gives away where that child will be every Tuesday at 4pm. A conference video gives away enough voice to clone it. A public job title gives away who approves the payments. Put together, these become the script for a "family emergency" call or a fake payment request.

Families can't see this picture of themselves. Your job is to build the tool that shows them, **for their own family only**, in plain language, with a fix list a busy parent can act on tonight.

## The challenge

Build a tool that:

1. **Discovers** a family's public exposures, using only identifiers the family has verified
2. **Explains** each risk in 2 calm sentences a non-technical parent understands, ideally in Arabic and English, using an **open-weight model** (Gemma 4 via the Gemini API, or a model running locally)
3. **Protects**: a prioritised, practical fix list

You start with a working pipeline that already finds the easy things. The hard, human-impact risks are left for you.

## Quickstart (5 minutes, no installs)

Python 3.10+ only. No dependencies.

```bash
git clone <this repo> && cd family-footprint
python -m footprint scan-all          # scan the two synthetic families
python eval/score.py                  # score yourself
python -m unittest discover tests     # privacy guardrails must pass
```

You should see **TOTAL: 58.7 / 100**. That's the baseline to beat. Open `out/fam-001.report.md` to see the report a parent would get.

### Add an open-weight model

```bash
# Option A: Gemma 4 through the Gemini API (free key from Google AI Studio)
export GEMINI_API_KEY=<your-key>
python -m footprint scan-all --llm gemini                # default model: gemma-4-26b-a4b-it
python -m footprint scan-all --llm gemini --lang ar
export FOOTPRINT_MODEL=gemma-4-31b-it                    # optional: the larger Gemma 4

# Option B: run a model locally with Ollama (download it at home, not on venue Wi-Fi)
ollama pull falcon3                   # or qwen2.5, llama3.2, mistral ...
python -m footprint scan-all --llm ollama
python -m footprint scan-all --llm ollama --lang ar

# Option C: any OpenAI-compatible local server (llama.cpp, vLLM, LM Studio)
export FOOTPRINT_LLM_URL=http://localhost:8080/v1/chat/completions
export FOOTPRINT_MODEL=<your-model>
python -m footprint scan-all --llm openai
```

Running locally (Gemma, Falcon from Abu Dhabi's TII, or any open-weight model) means family data never leaves the device, and that earns extra credit under Privacy by design. Never commit your API key.

## What you're working with

```
data/synthetic/
  families/     fam-001 (Haddad), fam-002 (Mensah-Rao): members, roles, consent, verified identifiers
  world/        the synthetic "internet": breaches, social profiles, posts, photo EXIF,
                people-search listings, places
eval/
  answer_keys/  what a perfect scan finds for the public families
  score.py      the auto-scorer
footprint/
  consent.py    consent rules + PrivacyGuard   <- do not weaken
  linker.py     links world records to members via VERIFIED identifiers only
  detectors/
    baseline.py   5 working detectors (with known gaps)
    challenge.py  4 empty detectors (yours to build)
  explain.py    template / Ollama / OpenAI-compatible local model
  playbook.py   fix actions per risk
  report.py     findings JSON + parent-friendly Markdown report
docs/           data model, judging, ideas
```

**Every person, email, phone number, company, school and breach in this repo is fictional.** Emails use reserved `example.*` domains, and map coordinates are deliberately placed at sea.

## The nine risks

| Category | What it means | Baseline |
|---|---|---|
| `CREDENTIAL_LEAK` | A family password leaked in a breach | ✅ works |
| `PERSONAL_DATA_LEAK` | A breach leaked phone, date of birth or address | ✅ works |
| `CONTACT_EXPOSED` | Phone/email listed publicly | ✅ works |
| `HOME_LOCATION` | Home can be located | ⚠️ photo GPS only |
| `ACCOUNT_LINKAGE` | One username ties accounts together | ⚠️ ignores minors |
| `CHILD_IDENTIFIABLE` | A child's full name + school are public | ❌ yours |
| `ROUTINE_PATTERN` | Same place, same weekday, same time | ❌ yours |
| `VOICE_CLONE_RISK` | Long public voice recordings | ❌ yours |
| `IMPERSONATION_TARGET` | Senior/finance role + family details = scam target | ❌ yours |

The hints are in `footprint/detectors/challenge.py`.

## Tracks

Pick one, or go for all of them.

- **Discover:** build the four missing detectors and fix the two weak ones. Measured by the auto-scorer.
- **Explain:** make the risk story genuinely good. Accurate, calm, no invented facts, bilingual Arabic/English.
- **Protect:** turn the report into something a parent would actually use: a one-page summary, a "fix it tonight" checklist, a family safe-word setup.
- **Bonus: Elders.** Design the experience for a grandparent who gets a cloned-voice call. What do they see, and what do they do?

## Rules

1. **Self-scan only.** Read [RESPONSIBLE_USE.md](RESPONSIBLE_USE.md). Never search the world by a person's name. Never report on a member who hasn't consented. The synthetic data contains **decoys** (people with the same name, a relative who hasn't accepted the invite), and **the scorer penalises you for touching them.**
2. **Open-weight models only.** During the hackathon, models may run locally or through the Gemini API, because all data is synthetic. Any real-world version must keep family data on-device or self-hosted, so say in your demo how you'd get there. Coding assistants for *writing* your code are fine.
3. **Keep the contract.** Organizers will run your fork on a **hidden family** with this exact command, so keep it working:
   ```bash
   python -m footprint scan --family <file> --world data/synthetic/world --world <hidden-world> --out <dir>
   ```
   Output must stay `<dir>/<family_id>.findings.json` in the current format (see [docs/data-model.md](docs/data-model.md)).
4. **Privacy tests must pass**: `python -m unittest discover tests`.
5. **No real people.** Don't add real names, real accounts or real addresses to the repo, your demo or your slides.

## Judging

| Criterion | Weight | How |
|---|---|---|
| Hidden-family score | 40% | `eval/score.py` on a family you've never seen |
| Explanation quality | 20% | Accurate, calm, useful. Bonus for Arabic. |
| Parent experience | 20% | Could a busy, non-technical parent act on it tonight? |
| Privacy by design | 20% | Consent, data minimisation, a path to on-device inference, no decoy leaks |

A privacy violation on the hidden family scores **0 on Privacy by design**. Full details are in [docs/judging.md](docs/judging.md).

## Prizes you can stack

One project can compete for this challenge **and** the event's MLH prizes:

| Prize | How Family Footprint fits |
|---|---|
| **Best Use of Gemma 4** | Use `--llm gemini` (Gemma 4 through the Gemini API) for explanations, post classification or the routine and school detectors |
| **Best Open-Source AI Project** | Apache-2.0 repo, open-weight models, privacy-first design |
| **Best Innovation in Your Language** | The Arabic track: risk explanations parents can read in their own language. Check the sponsor's brief for what they're judging. |

## Submitting

Before code freeze:
1. Push your fork and share the link with organizers
2. Commit `out/` from `python -m footprint scan-all`
3. Fill in [SUBMISSION.md](SUBMISSION.md): team, model used, what you built, what you'd do next

## About

Family Footprint is an open challenge by **CysuiteONE**, a UAE cybersecurity-as-a-service company that helps growing businesses stay cyber, AI and privacy ready with a dedicated advisor. Attackers increasingly reach a company through the people around it. This challenge starts at home.

Licensed under [Apache 2.0](LICENSE).
