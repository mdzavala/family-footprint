"""Turn findings into a short, calm risk story using an OPEN-WEIGHT model (Gemma via the
Gemini API, or any open model running locally).

Backends (set with --llm):
  template  no model, built-in English sentences (default, always works)
  gemini    Gemma 4 through the Gemini API (Google AI Studio key in GEMINI_API_KEY)
            default model gemma-4-26b-a4b-it; also gemma-4-31b-it
  ollama    Ollama on http://localhost:11434  (any open-weight model you pulled)
  openai    any OpenAI-compatible local server: llama.cpp, vLLM, LM Studio
            (set FOOTPRINT_LLM_URL, e.g. http://localhost:8080/v1/chat/completions)

Model name: FOOTPRINT_MODEL (defaults: gemini -> gemma-4-26b-a4b-it, others -> falcon3).

Data minimisation: the prompt never includes emails, phone numbers or usernames.
Only the category, the person's role and age band, and short evidence descriptions.
"""
import json
import os
import urllib.request

ROLE_WORDS = {"guardian": "a parent", "adult": "an adult", "child": "a child", "elder": "a grandparent"}

TEMPLATES = {
    "CREDENTIAL_LEAK": "A password used by {who} was leaked in a data breach. Criminals try leaked passwords on email and banking first.",
    "PERSONAL_DATA_LEAK": "Personal details of {who} leaked in a breach. Scammers use them to sound convincing on the phone.",
    "CONTACT_EXPOSED": "The phone number or email of {who} is publicly listed, which makes targeted scam calls easy.",
    "HOME_LOCATION": "Someone could work out where {who} lives from what is public online.",
    "ACCOUNT_LINKAGE": "The same username connects accounts of {who}, so a private account can be traced back to them.",
    "CHILD_IDENTIFIABLE": "A stranger could find {who}'s full name and school from public posts.",
    "ROUTINE_PATTERN": "Public posts reveal where {who} is at the same time every week.",
    "VOICE_CLONE_RISK": "There are long public recordings of {who}'s voice. That is enough to clone it for a fake emergency call.",
    "IMPERSONATION_TARGET": "{who_cap} has a public senior role and public family details, a common setup for payment or 'family emergency' scams.",
}


def describe_evidence(ctx, ids):
    idx = ctx.world["index"]
    lines = []
    for i in ids:
        r = idx.get(i, {})
        if "breach" in r:
            lines.append(f"breach '{r['breach']}' exposing {', '.join(r['data_classes'])}")
        elif "text" in r:
            lines.append(f"public post: \"{r['text']}\"")
        elif "platform" in r:
            lines.append(f"public {r['platform']} profile, bio: \"{r.get('bio', '')}\"")
        elif "site" in r:
            lines.append(f"people-search listing on {r['site']}")
        elif "exif" in r:
            lines.append("photo with embedded GPS location")
    return lines


def _template(finding, member):
    who = ROLE_WORDS.get(member["role"], "a family member")
    return TEMPLATES.get(finding.category, "{who_cap} has an online exposure.").format(
        who=who, who_cap=who[0].upper() + who[1:])


def _prompt(finding, member, evidence_lines, lang):
    language = "Arabic" if lang == "ar" else "English"
    return (
        "You are a calm family-safety advisor. Write 2 short sentences in " + language +
        " for a non-technical parent. Explain the risk and why it matters. Do not exaggerate,"
        " do not invent facts beyond the evidence, and do not include any names.\n"
        f"Risk category: {finding.category}\nPerson: {ROLE_WORDS.get(member['role'])}, "
        f"age band {member['age_band']}\nEvidence:\n- " + "\n- ".join(evidence_lines)
    )


GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _post(url, payload, headers=None):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def explain(finding, ctx, backend="template", lang="en"):
    member = ctx.member(finding.member_id)
    if backend == "template":
        return _template(finding, member)
    prompt = _prompt(finding, member, describe_evidence(ctx, finding.evidence), lang)
    default_model = "gemma-4-26b-a4b-it" if backend == "gemini" else "falcon3"
    model = os.environ.get("FOOTPRINT_MODEL", default_model)
    try:
        if backend == "gemini":
            key = os.environ.get("GEMINI_API_KEY")
            if not key:
                raise RuntimeError("set GEMINI_API_KEY (free key from Google AI Studio)")
            res = _post(GEMINI_URL.format(model=model),
                        {"contents": [{"parts": [{"text": prompt}]}]},
                        headers={"x-goog-api-key": key})
            parts = res["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
        if backend == "ollama":
            url = os.environ.get("FOOTPRINT_LLM_URL", "http://localhost:11434/api/generate")
            return _post(url, {"model": model, "prompt": prompt, "stream": False})["response"].strip()
        if backend == "openai":
            url = os.environ.get("FOOTPRINT_LLM_URL", "http://localhost:8080/v1/chat/completions")
            res = _post(url, {"model": model, "messages": [{"role": "user", "content": prompt}]})
            return res["choices"][0]["message"]["content"].strip()
    except Exception as e:  # keep the demo alive if the model is down
        return _template(finding, member) + f" [model unavailable: {e.__class__.__name__}]"
    raise ValueError(f"unknown backend {backend}")
