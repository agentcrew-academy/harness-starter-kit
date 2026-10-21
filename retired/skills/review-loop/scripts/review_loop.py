#!/usr/bin/env python3
"""review_loop -- keeps "a human reviewing a long AI-written document" from
drifting between revisions.

Pure standard library, nothing to install.

It does exactly one thing: make the number of changes that actually happened
equal the number of changes the reviewer actually saw. Drift is defined as
those two numbers not matching -- something changed, or an entire section
vanished, and the reviewer never knew.

Three commands:

  render <doc.md>    Render the document into a reviewable web page (one
                      comment box per block) and record this version's state
  check <doc.md>      Pre-publish gate. Exits non-zero on coverage gaps,
                      tampered approvals, implicit inheritance, or
                      duplicated numbers
  apply <doc.md> <feedback.txt>   Consume review feedback, update each
                      block's status, print the to-do list

Document format: mark each block with a one-line comment holding its
permanent id.

    <!-- @block intro -->
    ## What this document is
    body...

    <!-- @block timeline -->
    ## Timeline
    body...

Ids (intro, timeline) are assigned once at birth and **never change after
that**. Headings can change, order can change, the body can be rewritten
entirely -- the id follows that block of content.
The displayed numbering is generated at render time; never hand-write it.

To remove a block, don't just delete it -- that would make it vanish from
the review flow entirely, not rejected, just never seen by anyone. Leave one
line instead:

    <!-- @block old-section removed: folded into timeline, this call no longer applies -->

Status is never hand-written; this script computes all of it (by comparing
content hashes):

  new        appeared for the first time in this version
  edited     content differs from the previous version
  unchanged  content is byte-for-byte identical to the previous version
  approved   the reviewer approved it, and it hasn't been touched since
  removed    explicitly removed; rendered greyed-out but still in the document

State lives in <doc>.review-state.json. That file is an **artifact, not a
source document** -- don't hand-edit it.
"""

import argparse
import hashlib
import html
import json
import os
import re
import sys
from datetime import datetime, timezone

BLOCK_RE = re.compile(
    r"^[ \t]*<!--[ \t]*@block[ \t]+([A-Za-z0-9][A-Za-z0-9_-]*)"
    r"(?:[ \t]+removed[ \t]*:[ \t]*(.*?))?[ \t]*-->[ \t]*$"
)

# Implicit inheritance: a block that only makes sense by pointing at another
# block will rot the moment that reference does -- and once the referenced
# version is archived, the "final" copy is crippled. Every block has to
# stand on its own.
INHERIT_PATTERNS = [
    (r"same as v\d", "same as vN"),
    (r"same as (?:the )?previous version", "same as previous version"),
    (r"see (?:the )?previous section", "see previous section"),
    (r"can be skipped", "can be skipped"),
    (r"unchanged from v\d", "unchanged from vN"),
    (r"same as (?:above|previous)", "same as above"),
]

NUMBER_RE = re.compile(
    r"(?:NT\$|US\$|\$|USD|TWD)\s?[\d,]+(?:\.\d+)?"          # currency amounts
    r"|\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b"                     # comma-grouped
    r"|\b\d+\s*(?:minutes?|hours?|people|days?|weeks?|months?|%)"  # unit-bearing
)

STATUS_ORDER = ["new", "edited", "unchanged", "approved", "removed"]
STATUS_LABEL = {
    "new": "New",
    "edited": "Edited",
    "unchanged": "Unchanged",
    "approved": "Approved",
    "removed": "Removed",
}

DEFAULT_MIN_COVERAGE = 1.0  # every block from the previous version must have
                             # a known fate (present, or explicitly removed)


# ---------------------------------------------------------------- parsing

def sha(text):
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


def first_heading(body):
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    for line in body.splitlines():
        if line.strip():
            return line.strip()[:40]
    return ""


def parse(path):
    """Read the markdown, split it into blocks. Returns (preamble, [block,...])."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    blocks, preamble, cur, seen = [], [], None, {}
    for lineno, line in enumerate(lines, 1):
        m = BLOCK_RE.match(line)
        if not m:
            (cur["lines"] if cur else preamble).append(line)
            continue
        bid, removed_reason = m.group(1), m.group(2)
        if bid in seen:
            sys.exit(f"Error: duplicate block id '{bid}' (line {seen[bid]} and line {lineno})."
                     f"\nAn id is an identity -- it must be unique.")
        seen[bid] = lineno
        cur = {"id": bid, "lineno": lineno, "lines": [],
               "removed_reason": (removed_reason or "").strip() or None}
        blocks.append(cur)

    for b in blocks:
        b["body"] = "\n".join(b["lines"]).strip()
        b["hash"] = sha(b["body"])
        b["title"] = b["removed_reason"] and f"(Removed) {b['id']}" or first_heading(b["body"])
    return "\n".join(preamble).strip(), blocks


def state_path(doc):
    return os.path.splitext(doc)[0] + ".review-state.json"


def load_state(doc):
    p = state_path(doc)
    if not os.path.exists(p):
        return {"schema_version": 1, "doc": os.path.basename(doc),
                "current_version": 0, "blocks": {}}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_state(doc, st):
    with open(state_path(doc), "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ---------------------------------------------------------------- status computation

def compute(blocks, st, bump=False):
    """Diff hashes to work out each block's status for this version. bump=True writes the new state back."""
    prev = st.get("blocks", {})
    version = st.get("current_version", 0) + (1 if bump else 0)
    version = max(version, 1)
    out = []

    for b in blocks:
        rec = prev.get(b["id"])
        if b["removed_reason"]:
            status = "removed"
        elif rec is None:
            status = "new"
        elif rec.get("status") == "removed":
            status = "new"            # removed then brought back -- treat as new
        elif rec.get("hash") != b["hash"]:
            status = "edited"
        elif rec.get("approved_hash") == b["hash"]:
            status = "approved"
        else:
            status = "unchanged"

        b["status"] = status
        b["first_seen"] = (rec or {}).get("first_seen", version)
        b["approved_hash"] = (rec or {}).get("approved_hash")
        b["prev_hash"] = (rec or {}).get("hash")
        out.append(b)

    if bump:
        newblocks = {}
        for b in out:
            rec = dict(prev.get(b["id"], {}))
            rec.update({"hash": b["hash"], "status": b["status"],
                        "first_seen": b["first_seen"], "title": b["title"]})
            if b["removed_reason"]:
                rec["removed_reason"] = b["removed_reason"]
            newblocks[b["id"]] = rec
        # a block that existed last version and is entirely gone this version
        # gets a forced tombstone, so it can't quietly disappear
        for bid, rec in prev.items():
            if bid not in newblocks:
                rec = dict(rec)
                rec["status"] = "vanished"
                newblocks[bid] = rec
        st["blocks"] = newblocks
        st["current_version"] = version
        st["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return version, out


# ---------------------------------------------------------------- checks

def coverage(prev_blocks, cur_ids):
    """Of the previous version's blocks, how many have a known fate in this
    version (still present, or explicitly marked removed).

    This is the single most important number in the script. Sending an agent
    to "look for anything missing" is never reliable; turning it into a
    ratio with a denominator means a missing block always shows up as the
    ratio dropping, with no human "noticing" required.
    """
    live = [bid for bid, rec in prev_blocks.items() if rec.get("status") != "vanished"]
    if not live:
        return 1.0, [], 0, 0
    missing = [bid for bid in live if bid not in cur_ids]
    matched = len(live) - len(missing)
    return matched / len(live), missing, matched, len(live)


def check(doc, min_cov=DEFAULT_MIN_COVERAGE, strict_numbers=False):
    st = load_state(doc)
    _, blocks = parse(doc)
    version, blocks = compute(blocks, st, bump=False)
    cur_ids = {b["id"] for b in blocks}
    errors, warns = [], []

    # 1. coverage: nothing from the previous version disappears silently
    cov, missing, matched, total = coverage(st.get("blocks", {}), cur_ids)
    if total:
        line = f"coverage {cov:.3f} ({matched}/{total}, threshold {min_cov})"
        if cov < min_cov:
            errors.append(f"{line}\n     Blocks present last version but missing now: {', '.join(missing)}"
                          f"\n     To remove one, leave a line <!-- @block <id> removed: reason -->. Don't just delete it.")
        else:
            print(f"  ok   {line}")

    # 2. an approved block got changed without anyone saying so
    tampered = [b for b in blocks
                if b["approved_hash"] and b["hash"] != b["approved_hash"]
                and b["status"] != "removed"]
    if tampered:
        errors.append("Approved blocks changed after approval: " + ", ".join(b["id"] for b in tampered) +
                      "\n     Approval freezes the content at that moment. Changing it means resubmitting for review, not silently editing it.")
    else:
        napp = sum(1 for b in blocks if b["status"] == "approved")
        print(f"  ok   {napp} approved block(s), content still matches what was approved")

    # 3. implicit inheritance: every block has to stand on its own
    hits = []
    for b in blocks:
        for pat, label in INHERIT_PATTERNS:
            if re.search(pat, b["body"], re.IGNORECASE):
                hits.append(f"{b['id']} ({label})")
                break
    if hits:
        errors.append("Wording that points to another version or section (implicit inheritance): " + ", ".join(hits) +
                      "\n     This kind of reference rots after a revision or archiving. Every block has to say the whole thing itself.")
    else:
        print("  ok   no implicit-inheritance wording found")

    # 4. the same number written in two places (they'll drift into two stories)
    where = {}
    for b in blocks:
        if b["status"] == "removed":
            continue
        for n in set(NUMBER_RE.findall(b["body"])):
            where.setdefault(n.strip(), set()).add(b["id"])
        # ignore plain narrative digits, only track ones with a unit or currency
    dupes = {n: ids for n, ids in where.items() if len(ids) > 1}
    if dupes:
        msg = "The same number shows up in more than one block (they'll drift apart):\n" + "\n".join(
            f"     {n} -> {', '.join(sorted(ids))}" for n, ids in sorted(dupes.items())[:12])
        (errors if strict_numbers else warns).append(msg)
    else:
        print("  ok   no number appears in more than one block")

    print()
    for w in warns:
        print(f"  NOTE {w}")
    for e in errors:
        print(f"  FAIL {e}")
    if errors:
        print(f"\nFailed. {len(errors)} issue(s) to fix.")
        return 1
    print("Passed." + (" (notes above, not blocking release)" if warns else ""))
    return 0


# ---------------------------------------------------------------- rendering

def md_lite(text):
    """Turn a block's body into just-enough HTML. Deliberately not full markdown -- this is a review page, not a publication."""
    out, in_ul, in_code = [], False, False
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.strip().startswith("```"):
            out.append("</pre>" if in_code else "<pre>")
            in_code = not in_code
            continue
        if in_code:
            out.append(html.escape(line))
            continue
        if not line.strip():
            if in_ul:
                out.append("</ul>"); in_ul = False
            continue
        esc = html.escape(line)
        esc = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc)
        esc = re.sub(r"`(.+?)`", r"<code>\1</code>", esc)
        m = re.match(r"^(#{1,6})\s+(.*)$", esc)
        if m:
            if in_ul:
                out.append("</ul>"); in_ul = False
            lvl = min(len(m.group(1)) + 1, 6)
            out.append(f"<h{lvl}>{m.group(2)}</h{lvl}>")
            continue
        if re.match(r"^\s*[-*]\s+", esc):
            if not in_ul:
                out.append("<ul>"); in_ul = True
            out.append("<li>" + re.sub(r"^\s*[-*]\s+", "", esc) + "</li>")
            continue
        if in_ul:
            out.append("</ul>"); in_ul = False
        out.append(f"<p>{esc}</p>")
    if in_ul:
        out.append("</ul>")
    if in_code:
        out.append("</pre>")
    return "\n".join(out)


def render(doc, out_path=None, title=None):
    st = load_state(doc)
    preamble, blocks = parse(doc)
    prev_ids = set(st.get("blocks", {}))
    version, blocks = compute(blocks, st, bump=True)
    cov, missing, matched, total = coverage(
        {k: v for k, v in st["blocks"].items() if k in prev_ids},
        {b["id"] for b in blocks})

    here = os.path.dirname(os.path.abspath(__file__))
    tpl_path = os.path.join(here, "..", "assets", "template.html")
    if not os.path.exists(tpl_path):                       # fallback if the script gets moved on its own
        tpl_path = os.path.join(here, "template.html")
    with open(tpl_path, encoding="utf-8") as f:
        tpl = f.read()

    counts = {s: sum(1 for b in blocks if b["status"] == s) for s in STATUS_ORDER}
    changed = counts["new"] + counts["edited"] + counts["removed"]

    cards = []
    for i, b in enumerate(blocks, 1):
        cards.append(
            '<section class="blk s-{st}" data-id="{id}" data-status="{st}">'
            '<div class="bhead"><span class="num">{i:02d}</span>'
            '<span class="btitle">{title}</span>'
            '<span class="badge">{lab}</span>'
            '<code class="bid">{id}</code></div>'
            '{rm}<div class="body">{body}</div>'
            '<div class="cmt"><div class="intent">'
            '<label><input type="radio" name="i-{id}" value="Approve">Approve</label>'
            '<label><input type="radio" name="i-{id}" value="Revise">Revise</label>'
            '<label><input type="radio" name="i-{id}" value="Question">Question</label>'
            '<label><input type="radio" name="i-{id}" value="Discuss">Discuss</label>'
            '</div><textarea data-for="{id}" rows="2" '
            'placeholder="Your comment on this block (blank = no comment)"></textarea></div>'
            '</section>'.format(
                id=html.escape(b["id"]), st=b["status"], i=i,
                title=html.escape(b["title"] or b["id"]),
                lab=STATUS_LABEL[b["status"]],
                rm=('<p class="rmwhy">Removal reason: %s</p>' % html.escape(b["removed_reason"]))
                   if b["removed_reason"] else "",
                body=md_lite(b["body"]) if not b["removed_reason"] else ""))

    filled = (tpl
              .replace("{{TITLE}}", html.escape(title or os.path.basename(doc)))
              .replace("{{VERSION}}", str(version))
              .replace("{{PREAMBLE}}", md_lite(preamble) if preamble else "")
              .replace("{{COVERAGE}}", f"{cov:.1%}" if total else "--")
              .replace("{{COVDETAIL}}", f"{matched}/{total}" if total else "first version")
              .replace("{{CHANGED}}", str(changed))
              .replace("{{TOTAL}}", str(len(blocks)))
              .replace("{{CNEW}}", str(counts["new"]))
              .replace("{{CEDIT}}", str(counts["edited"]))
              .replace("{{CSAME}}", str(counts["unchanged"] + counts["approved"]))
              .replace("{{CREMOVED}}", str(counts["removed"]))
              .replace("{{BLOCKS}}", "\n".join(cards)))

    out_path = out_path or f"{os.path.splitext(doc)[0]}-review-v{version}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(filled)
    save_state(doc, st)

    print(f"Review page v{version}: {out_path}")
    print(f"  Blocks {len(blocks)} | New {counts['new']}  Edited {counts['edited']}  "
          f"Unchanged {counts['unchanged'] + counts['approved']}  Removed {counts['removed']}")
    if total:
        print(f"  Coverage {cov:.1%} ({matched}/{total})" +
              ("" if not missing else f"  Missing: {', '.join(missing)}"))
    return 0


# ---------------------------------------------------------------- feedback

FB_RE = re.compile(r"^\s*\[([A-Za-z0-9][A-Za-z0-9_-]*)\]\s*(Approve|Revise|Question|Discuss)\s*(?:[—\-–:]\s*(.*))?$")


def apply_fb(doc, fb_path):
    st = load_state(doc)
    _, blocks = parse(doc)
    compute(blocks, st, bump=False)
    byid = {b["id"]: b for b in blocks}

    with open(fb_path, encoding="utf-8") as f:
        raw = f.read()

    items, unknown = [], []
    for line in raw.splitlines():
        m = FB_RE.match(line)
        if not m:
            continue
        bid, intent, note = m.group(1), m.group(2), (m.group(3) or "").strip()
        if bid not in byid:
            unknown.append(bid)
            continue
        items.append({"id": bid, "intent": intent, "note": note})

    if not items:
        sys.exit("No feedback lines could be parsed. Format: [block-id] Approve|Revise|Question|Discuss -- note")

    for it in items:
        rec = st["blocks"].setdefault(it["id"], {})
        if it["intent"] == "Approve":
            rec["approved_hash"] = byid[it["id"]]["hash"]
            rec["approved_at_version"] = st.get("current_version")
            rec["status"] = "approved"
        rec["last_intent"] = it["intent"]
        if it["note"]:
            rec["last_note"] = it["note"]
    save_state(doc, st)

    todo = [i for i in items if i["intent"] != "Approve"]
    passed = [i for i in items if i["intent"] == "Approve"]

    print(f"Received {len(items)} feedback item(s). Approved {len(passed)}, to handle {len(todo)}.")
    if unknown:
        print(f"Note: unknown block id(s), skipped -> {', '.join(unknown)}")
    if passed:
        print(f"\nFrozen (later edits will be blocked by check): {', '.join(i['id'] for i in passed)}")
    if todo:
        print("\nTo do:")
        for i in todo:
            print(f"  [{i['id']}] {i['intent']}  {i['note'] or '(no note -- go ask before touching it)'}")
    silent = [b["id"] for b in blocks
              if b["status"] in ("new", "edited") and b["id"] not in {i["id"] for i in items}]
    if silent:
        print(f"\nThese blocks changed this version but got no feedback at all -- don't treat that as approval: {', '.join(silent)}")
    return 0


# ---------------------------------------------------------------- CLI

def main():
    ap = argparse.ArgumentParser(
        description="Keep a long document's multi-round review from drifting between revisions",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render", help="Render the review page and record this version")
    r.add_argument("doc"); r.add_argument("-o", "--out"); r.add_argument("-t", "--title")

    c = sub.add_parser("check", help="Pre-publish gate; exits non-zero on problems")
    c.add_argument("doc")
    c.add_argument("--min-coverage", type=float, default=DEFAULT_MIN_COVERAGE)
    c.add_argument("--strict-numbers", action="store_true",
                   help="Also fail (instead of just warn) when the same number appears in multiple blocks")

    a = sub.add_parser("apply", help="Consume review feedback, update state, print the to-do list")
    a.add_argument("doc"); a.add_argument("feedback")

    args = ap.parse_args()
    if not os.path.exists(args.doc):
        sys.exit(f"File not found: {args.doc}")

    if args.cmd == "render":
        return render(args.doc, args.out, args.title)
    if args.cmd == "check":
        print(f"Checking {args.doc}")
        return check(args.doc, args.min_coverage, args.strict_numbers)
    if args.cmd == "apply":
        return apply_fb(args.doc, args.feedback)


if __name__ == "__main__":
    sys.exit(main())
