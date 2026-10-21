#!/usr/bin/env python3
"""
redact.py — drop whole lines from the report, by keywords the user names.

Why this exists: it lets the user "tell the AI what to delete", instead of
"open the file and delete it yourself". Someone with zero technical
background may not be able to open a file, find a line, and save it — but
they can absolutely say "nothing related to hospitals" or "take out that
one site."

**This script's output never contains the deleted content.** It only
reports how many lines were removed and which keywords matched. So the AI
can run it without ever having seen the report, and only read the report
for the first time after the deletion has happened.
This is what makes the whole privacy promise hold up — it's guaranteed by
the process, not by the AI's self-restraint.

Usage:
  python3 redact.py --report ~/.info-diet/report.txt --terms "hospital,job search,some-site"
  python3 redact.py --report ... --terms "..." --dry-run    # preview line count only, no file changes
"""

import argparse
import os
import shutil
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, help="the report file to process")
    ap.add_argument("--terms", required=True,
                    help="keywords the user named to remove, comma-separated. Case-insensitive.")
    ap.add_argument("--dry-run", action="store_true",
                    help="only report how many lines would be removed, don't touch the file")
    args = ap.parse_args()

    path = os.path.expanduser(args.report)
    if not os.path.exists(path):
        print(f"Report file not found: {path}", file=sys.stderr)
        print("STATUS=nofile")
        return 1

    terms = [t.strip().lower() for t in args.terms.split(",") if t.strip()]
    if not terms:
        print("No keywords given, nothing to do.")
        print("STATUS=noterms")
        return 0

    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    kept, removed_by = [], {t: 0 for t in terms}
    for line in lines:
        low = line.lower()
        hit = next((t for t in terms if t in low), None)
        if hit:
            removed_by[hit] += 1
        else:
            kept.append(line)

    total_removed = len(lines) - len(kept)

    # Only report counts, never content. This line is the whole point of this script.
    print(f"Keywords given: {len(terms)}")
    for t in terms:
        print(f"  \"{t}\" matched {removed_by[t]} lines")
    print(f"Removed {total_removed} lines total, report went from {len(lines)} to {len(kept)} lines.")
    print("(The removed content is not printed here, and won't appear anywhere.)")

    if args.dry_run:
        print("This was a dry run — the file was not changed.")
        print("STATUS=dryrun")
        return 0

    if total_removed:
        shutil.copyfile(path, path + ".bak")
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(kept)
        # The backup file contains what was just deleted — keeping it would defeat the purpose. Remove it.
        os.remove(path + ".bak")

    print("STATUS=ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
