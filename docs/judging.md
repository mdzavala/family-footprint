# Judging

## 1. Hidden-family score (40%)
Organizers run your fork on a family you have never seen, merged with a hidden world file:
```bash
python -m footprint scan --family hidden/fam-XXX.json \
  --world data/synthetic/world --world hidden/world --out judged/
python eval/score.py --pred judged --keys hidden/answer_keys
```
How a family is scored (0-100):
- **Detection, up to 80 pts.** Each expected finding is worth its severity (low 1, medium 2, high 3, critical 4). It counts when your `category` + `member_id` match.
- **Severity, up to 20 pts.** The share of your correct findings that have the right severity.
- **Noise.** -5 per finding that isn't in the answer key.
- **Privacy.** -10 per finding about a non-consented member, or citing someone else's record.

The baseline scores about 59. A careful rule-based solution can reach 100. The hidden family uses the same nine categories.

## 2. Explanation quality (20%)
Judges read the `explanation` fields and the Markdown report.
- Accurate: nothing invented beyond the evidence
- Calm and specific: no fear-mongering, no jargon
- Bilingual Arabic/English earns a bonus
- Uses an open-weight model (Gemma via the Gemini API, or local)

## 3. Parent experience (20%)
Could a busy, non-technical parent understand the report in 2 minutes and fix the top 3 things tonight? Demos are welcome: a simple UI, a printable page, a WhatsApp-style summary.

## 4. Privacy by design (20%)
- Privacy tests pass. Strict mode doesn't raise on your detectors.
- No decoys or non-consented members in your findings. **Any violation on the hidden family scores 0 here.**
- Data minimisation: what you send to the model, what you store, how long you keep it
- A credible path to on-device inference for real families (running locally on the day scores best)
- Anything extra you designed: consent UX, guardian controls for teens, deletion

## Demo (3 minutes)
1 minute problem and approach, 1.5 minutes live run, 30 seconds on privacy. Use only the synthetic families.
