"""What-if simulator: which single improvement moves an AI readiness score the most?

For each dimension, simulates a one-point improvement on every answer and reports the gain
in the final (capped) score. Also simulates fixing the data-handling flag. The ranking often
surprises teams: when the cap is active, most training adds exactly zero.
Standard library only. Uses the scoring model in readiness.py.
"""
import copy
import json
import sys

from readiness import DIMENSIONS, overall


def bump(answers, dim, step=1):
    a = copy.deepcopy(answers)
    for item in a[dim]:
        if item.get("reverse"):
            item["value"] = max(1, item["value"] - step)
        else:
            item["value"] = min(5, item["value"] + step)
    return a


def simulate(profile):
    flags = profile.get("flags", [])
    base = overall(profile["answers"], flags)["score"]
    rows = []
    for dim, (label, _) in DIMENSIONS.items():
        new = overall(bump(profile["answers"], dim), flags)["score"]
        rows.append((new - base, f"+1 on {label}"))
    if "data_handling_risk" in flags:
        cleared = [f for f in flags if f != "data_handling_risk"]
        fixed = bump(profile["answers"], "privacy", 2)
        rows.append((overall(fixed, cleared)["score"] - base, "Fix data handling (clear flag, +2 on privacy)"))
    return base, sorted(rows, reverse=True)


def main(path, name):
    with open(path, encoding="utf-8") as fh:
        profiles = {p["name"]: p for p in json.load(fh)}
    base, rows = simulate(profiles[name])
    print(f"{name}: {base}/100 today\n")
    for gain, what in rows:
        print(f"  {gain:+3d}  {what}")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0] if a else "examples/profiles.json", a[1] if len(a) > 1 else "Fast mover, loose guardrails")
