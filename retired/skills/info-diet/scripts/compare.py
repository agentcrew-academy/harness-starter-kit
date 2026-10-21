#!/usr/bin/env python3
"""
compare.py — diff against the previous baseline, spit out just five numbers.

Deliberately kept tiny. The value of the first check-in comes from "seeing
your own numbers for the first time" — every check-in after that only has
one job left: "did anything move." So a re-check doesn't need another long
report — five lines is enough. A long report would just make people not
want to run it a second time.

Usage:
  python3 compare.py --old ~/.info-diet/baseline-2026-08-12.json \
                     --new ~/.info-diet/baseline-2026-09-12.json
"""

import argparse
import json
import os
import sys


def pct(part, whole):
    return (part / whole * 100) if whole else 0.0


# Deliberately does "not" judge direction.
#
# The first version had all five metrics set so "decrease = improvement",
# including "external intake share" and "average daily visits". That
# smuggled in the value judgment "less is better" — which is exactly what
# the information diet concept (Clay Johnson) explicitly argues against:
# he says the problem isn't quantity, it's selection. It also directly
# contradicts what this tool's own docs say elsewhere ("always give the
# clean archetype honestly," "a single deep well isn't necessarily bad").
#
# This is a scale, not a personal trainer. A scale only reports the number.
# Which direction counts as progress is something the user decides for
# themselves, in conversation.
FLAT_BAND = 1.0   # within one percentage point counts as unchanged; month-to-month noise shouldn't be called "improvement"


def moved(delta, unit):
    if unit == "%":
        return "flat" if abs(delta) < FLAT_BAND else f"{delta:+.1f} pts"
    return "flat" if abs(delta) < 5 else f"{delta:+.0f}"


def load(path):
    p = os.path.expanduser(path)
    if not os.path.exists(p):
        print(f"Baseline file not found: {p}", file=sys.stderr)
        print("STATUS=nofile")
        sys.exit(1)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True, help="the previous baseline JSON")
    ap.add_argument("--new", required=True, help="this run's baseline JSON")
    args = ap.parse_args()

    a, b = load(args.old), load(args.new)

    if a.get("window_days") != b.get("window_days"):
        print(f"Note: the two runs used different windows ({a.get('window_days')} days vs "
              f"{b.get('window_days')} days), so the comparison will be skewed.")
        print()

    ta, tb = a["total_visits"], b["total_visits"]

    def bucket_pct(d, name):
        return pct(d.get("buckets", {}).get(name, 0), d["total_visits"])

    def feed_pct(d):
        known = d.get("feed_visits", 0) + d.get("detail_visits", 0)
        return pct(d.get("feed_visits", 0), known)

    metrics = [
        ("Watching-yourself share", bucket_pct(a, "self"), bucket_pct(b, "self"), "%"),
        ("External intake share", bucket_pct(a, "consume"), bucket_pct(b, "consume"), "%"),
        ("Scroll-without-clicking rate", feed_pct(a), feed_pct(b), "%"),
        ("00:00-05:00 share", pct(a.get("late_night_visits", 0), ta),
         pct(b.get("late_night_visits", 0), tb), "%"),
        ("Average daily visits", ta / max(a.get("days_covered", 1), 1),
         tb / max(b.get("days_covered", 1), 1), "visits"),
    ]

    print("=" * 60)
    print(f"Information diet re-check   {a['generated_at'][:10]}  ->  {b['generated_at'][:10]}")
    print("=" * 60)
    for name, old, new, unit in metrics:
        if unit == "%":
            line = f"  {name:<28}{old:5.1f}% -> {new:5.1f}%"
        else:
            line = f"  {name:<28}{old:5.0f} -> {new:5.0f} {unit}"
        print(f"{line:<58}{moved(new - old, unit)}")
    print()
    print("This only reports numbers, it doesn't judge good or bad.")
    print("Which direction counts as progress depends on what you set for yourself last time —")
    print("a smaller number isn't automatically good, and a bigger one isn't automatically bad.")
    print("STATUS=ok")


if __name__ == "__main__":
    main()
