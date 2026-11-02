"""AI readiness score for CRM teams, as a command-line tool.

10 weighted dimensions based on ADKAR, OECD and the NIST AI RMF (the same model as the
AI Readiness Calculator web app). Answers are 1-5. One rule matters more than any weight:
if the data-handling risk flag is raised, the score is capped at 59 until it is fixed.
Standard library only.
"""
import json
import sys

DIMENSIONS = {
    "awareness": ("AI awareness", 8),
    "attitude": ("Attitude and willingness", 10),
    "skills": ("Practical AI skills", 12),
    "prompting": ("Prompting and verification", 12),
    "role_fit": ("Role and use-case fit", 10),
    "privacy": ("Data privacy and responsible AI", 14),
    "support": ("Access and organisational support", 10),
    "confidence": ("Confidence without over-reliance", 8),
    "applying": ("Applying AI to real work", 10),
    "learning": ("Continuous learning", 6),
}
LEVELS = [(90, "AI Champion"), (75, "AI Confident"), (60, "AI Practitioner"), (40, "AI Aware"), (0, "AI Beginner")]
GOVERNANCE_CAP = 59


def item_score(value, reverse=False):
    v = 6 - value if reverse else value
    return (v - 1) / 4 * 100


def dimension_scores(answers):
    out = {}
    for dim in DIMENSIONS:
        items = answers[dim]
        out[dim] = sum(item_score(i["value"], i.get("reverse", False)) for i in items) / len(items)
    return out


def overall(answers, flags=()):
    ds = dimension_scores(answers)
    raw = sum(ds[d] * DIMENSIONS[d][1] for d in DIMENSIONS) / 100
    capped = "data_handling_risk" in flags and raw > GOVERNANCE_CAP
    score = GOVERNANCE_CAP if capped else raw
    level = next(name for floor, name in LEVELS if score >= floor)
    return {"score": round(score), "raw": round(raw), "capped": capped, "level": level, "dimensions": ds}


def main(path):
    with open(path, encoding="utf-8") as fh:
        profiles = json.load(fh)
    for p in profiles:
        r = overall(p["answers"], p.get("flags", []))
        note = f" (raw {r['raw']}, capped by data-handling flag)" if r["capped"] else ""
        print(f"{p['name']:<30} {r['score']:>3}/100  {r['level']}{note}")
        weakest = sorted(r["dimensions"].items(), key=lambda kv: kv[1])[:2]
        print(f"{'':<30} weakest: " + ", ".join(f"{DIMENSIONS[d][0]} ({v:.0f})" for d, v in weakest))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "examples/profiles.json")
