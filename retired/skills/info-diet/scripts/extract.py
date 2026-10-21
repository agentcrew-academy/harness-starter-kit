#!/usr/bin/env python3
"""
extract.py — aggregate browsing history into statistics that are safe to hand to an AI.

Privacy design (this is the reason this script exists, not a bolt-on feature):
  - Full URLs are "never" included in the output. URLs live in memory only for
    the duration of a single row, then get discarded.
  - The output has exactly three kinds of data: domain, path shape (all IDs
    and parameters stripped out), and counts/timestamps.
  - Search keywords are "not" output by default (of everything in the raw
    data, that's the single best way to reconstruct someone's personal
    situation). Only emitted with --with-search, and even then flagged
    separately so the user can decide whether to hand it over.

Two things that were verified empirically (don't revert these):
  1. Classification has to run "per visit", not per domain.
     The same domain can be both "watching yourself" and "external intake" —
     e.g. on Threads, /activity is your notifications, / is your feed.
     Majority-voting by domain buries this finding entirely.
  2. Chrome's visit_duration can't be used as time-on-page.
     It counts a tab sitting open with nobody looking at it. Summed up,
     it comes out to way more than 24 hours a day in practice.
     So this script only ever uses visit counts and active-day counts —
     it never outputs any duration figure.

Usage:
  python3 extract.py --db ~/.info-diet/history.db --days 30 \
      --report ~/.info-diet/report.txt --out ~/.info-diet/baseline.json

  # Confirmed personal accounts. "platform:@handle" is more accurate than
  # just "@handle", because the same name can belong to someone else on a
  # different platform.
  python3 extract.py --db ... --self "threads.com:@yourname,youtube.com:@YourChannel"
"""

import argparse
import collections
import datetime
import json
import os
import re
import sqlite3
import sys

# Chrome timestamp: microseconds since 1601-01-01. Subtract this offset to get Unix epoch.
WEBKIT_TO_UNIX = 11_644_473_600

# Low 8 bits of transition = how this visit happened. 3 = an auto-loaded
# iframe, not something the person clicked — always excluded, otherwise ads
# and trackers flood the stats.
TRANSITION_AUTO_SUBFRAME = 3

# "Watching yourself" path signature: notifications, inbox, and other
# self-monitoring entry points besides DMs.
SELF_PATH_PAT = re.compile(
    r"^/(activity|notifications?|inbox|mentions|alerts|me|dashboard|analytics|insights)\b",
    re.I,
)
# Creator / business dashboard domain signature.
SELF_HOST_PAT = re.compile(
    r"^(studio\.|creator\.|business\.|analytics\.|partner\.)", re.I
)
# Paths that are "still in the feed layer": home, recommended feed, explore, search results
FEED_PATHS = {
    "/", "/home", "/explore", "/feed", "/foryou", "/for-you", "/browse",
    "/trending", "/popular", "/timeline", "/following", "/discover", "/reels",
    "/shorts", "/search", "/search_result", "/results", "/hot", "/new", "/all",
}
# Tools & workbench: this isn't "information intake", it's getting things done
WORK_HOST_PAT = re.compile(
    r"^(mail\.|docs\.|drive\.|calendar\.|sheets\.|slides\.|meet\.|console\.|"
    r"accounts?\.|login\.|auth\.|admin\.|manager\.|app\.|api\.|dashboard\.|"
    r"localhost|127\.0\.0\.1)",
    re.I,
)
WORK_DOMAINS = {
    # Dev & productivity
    "github.com", "gitlab.com", "stackoverflow.com", "localhost", "127.0.0.1",
    "notion.so", "figma.com", "trello.com", "asana.com", "linear.app",
    "vercel.com", "netlify.com", "huggingface.co", "canva.com",
    # Search engines: a lookup tool, not an information source
    "google.com", "bing.com", "duckduckgo.com", "baidu.com", "yandex.com",
    "perplexity.ai",
    # AI tools
    "claude.ai", "chatgpt.com", "openai.com", "gemini.google.com",
    "aistudio.google.com", "poe.com", "grok.com",
}
# Messaging: one-on-one or group conversation, not information intake and not self-watching
COMMS_DOMAINS = {
    "messenger.com", "line.me", "whatsapp.com", "telegram.org", "slack.com",
    "discord.com", "teams.microsoft.com", "zoom.us", "wechat.com",
}
# Consumption platforms: this list is only a starting point — being
# incomplete is expected. Anything that doesn't hit gets bucketed as
# unclassified and handed to the AI + user to judge together. Local news,
# non-English platforms, and niche forums can never be fully covered by a
# hardcoded list.
CONSUME_DOMAINS = {
    "threads.com", "threads.net", "x.com", "twitter.com", "facebook.com",
    "instagram.com", "tiktok.com", "reddit.com", "youtube.com", "bilibili.com",
    "rednote.com", "xiaohongshu.com", "linkedin.com", "pinterest.com",
    "weibo.com", "news.ycombinator.com", "medium.com", "substack.com",
    "quora.com", "tumblr.com", "twitch.tv", "netflix.com", "9gag.com",
    "dcard.tw", "ptt.cc", "mobile01.com", "zhihu.com", "douyin.com",
}

# Path segments that look like IDs: pure digits, long hashes, UUIDs, overly long strings
ID_LIKE = re.compile(r"^([0-9]+|[0-9a-f]{8,}|[A-Za-z0-9_-]{16,})$")

# Sensitive categories that are auto-redacted by default.
#
# This is a safety net, not a guarantee. It will inevitably miss things —
# keyword matching can't catch a site it doesn't know about, or a service
# that uses a code name. The real protection is the earlier step of asking
# the user what to exclude; this list only catches what the user didn't
# think to mention.
# Anything caught here only shows up as a combined count under
# "sensitive category (auto-redacted)" — the domain name itself never appears.
SENSITIVE_PAT = re.compile(
    r"(porn|xvideo|xnxx|pornhub|onlyfans|hentai|nsfw|escort|adult|色情|成人影片|"
    r"tinder|bumble|hinge|grindr|okcupid|match\.com|交友|約會|"
    r"clinic|hospital|medical|health|patient|symptom|therapy|psychiatr|"
    r"cancer|hiv|std|醫院|診所|健保|症狀|心理諮商|"
    r"jobs?|hire|recruit|career|resume|cv|linkedin\.com/jobs|104\.com|1111\.com|"
    r"yourator|cakeresume|求職|人力銀行|履歷|"
    r"casino|bet|poker|lottery|gambl|娛樂城|博弈|"
    r"lawyer|legal|attorney|divorce|律師|離婚|訴訟|"
    r"loan|debt|bankrupt|貸款|債務|破產)",
    re.I,
)


def is_sensitive(host, title, extra_terms, auto_redact):
    """
    Decide whether this row gets auto-redacted outright. A redacted row
    doesn't even keep its domain name in the report.
    Two independent sources: the built-in list (can be turned off with
    --no-auto-redact), and the user's own named keywords (always active,
    can't be turned off).
    """
    blob = f"{host} {title or ''}"
    if auto_redact and SENSITIVE_PAT.search(blob):
        return True
    low = blob.lower()
    return any(t in low for t in extra_terms)

# These aren't handles, they're a site's own function pages. Without this
# filter, /user/profile would get mistaken for a person named "profile" and
# the user would get asked "is this your account?"
NOT_A_HANDLE = {
    "profile", "settings", "setting", "home", "me", "edit", "about", "login",
    "logout", "signup", "signin", "new", "search", "explore", "help", "account",
    "notifications", "messages", "inbox", "dashboard", "feed", "index",
}

BUCKETS = ("consume", "self", "comms", "work", "unclassified")
LABEL = {
    "consume": "External intake",
    "self": "Watching yourself",
    "comms": "Messaging",
    "work": "Tools & workbench",
    "unclassified": "Unclassified (needs a human call)",
}


def split_url(url):
    """
    Split a URL into (domain, list of path segments). Query strings and
    fragments are always dropped.
    Only http/https are kept: chrome-extension://, file://, about: aren't
    "browsing the web" — keeping them would just dump a pile of
    extension-ID-looking garbage into the unclassified list.
    """
    m = re.match(r"^https?://([^/?#]+)([^?#]*)", url, re.I)
    if not m:
        return None, []
    host = m.group(1).lower().split("@")[-1].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    segs = [s for s in (m.group(2) or "/").split("/") if s]
    return host, segs


def path_shape(segs, keep=2):
    """
    Collapse a path down to its "shape" — this is the key privacy step.
    /@someone/post/DMxK9    ->  /@someone/post
    /explore/6a6ac164000000   ->  /explore/:id
    Keeps only the first two segments; anything that looks like an ID gets replaced with :id.
    """
    if not segs:
        return "/"
    return "/" + "/".join(":id" if ID_LIKE.match(s) else s for s in segs[:keep])


def handle_of(segs):
    """Pull the account handle out of a path (/@name, /u/name, /user/name, /in/name)."""
    if not segs:
        return None
    first = segs[0]
    if first.startswith("@") and len(first) > 1:
        name = first[1:].lower()
        return None if name in NOT_A_HANDLE else "@" + name
    if first in ("u", "user", "users", "in", "profile", "c") and len(segs) > 1:
        name = segs[1].lower()
        if not ID_LIKE.match(segs[1]) and name not in NOT_A_HANDLE:
            return "@" + name
    return None


# Unread-count prefix on titles, e.g. "(3) Some article"
TITLE_PREFIX = re.compile(r"^\s*\(\d+\)\s*")
# Platform branding tacked onto the end of titles — useless for judging
# content quality, and reads better without it. Allows a bit of the
# platform's own marketing copy to trail after (e.g. Threads' ", Say more").
TITLE_SUFFIX = re.compile(
    r"\s*[\|/•\-–—]\s*(X|Twitter|Threads|YouTube|Facebook|Instagram|Reddit|"
    r"LinkedIn|Medium|小紅書|RedNote|bilibili)\b[^|/•]*$",
    re.I,
)
# Pure UI strings, not content. Keeping these would just turn "quality
# review" into "reading the menu bar."
TITLE_UI_ONLY = re.compile(
    r"^(messages?|inbox|notifications?|home|首頁|訊息|通知|收件匣|"
    r"explore|探索|search|搜尋|settings|設定|dashboard|log ?in|sign ?in)$",
    re.I,
)


def clean_title(title):
    t = (title or "").strip()
    t = TITLE_PREFIX.sub("", t)
    for _ in range(2):                 # some titles stack two layers of branding
        t = TITLE_SUFFIX.sub("", t).strip()
    t = t.strip(" -–—|•,")
    if TITLE_UI_ONLY.match(t):
        return ""
    return t if len(t) > 4 else ""


def base_domain(host):
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def classify(host, segs, shape, self_handles):
    """Return which bucket this single visit belongs to. Classified per visit, not per domain."""
    h = handle_of(segs)
    first = "/" + (segs[0] if segs else "")
    base = base_domain(host)

    # 1. Watching yourself: notifications page, dashboard, a confirmed personal account page
    if SELF_HOST_PAT.match(host):
        return "self"
    # A handle can be written as plain @xxx (matches on every platform), or
    # as threads.com:@xxx (only matches that one platform). The latter is
    # more accurate: the same name can belong to someone else elsewhere.
    if h and (h in self_handles or f"{host}:{h}" in self_handles):
        return "self"
    # A notification-shaped path only counts as "watching yourself" on
    # consumption platforms, otherwise a bank's /alerts or a dashboard's
    # /dashboard would get misclassified.
    if SELF_PATH_PAT.match(first) and (
        host in CONSUME_DOMAINS or base in CONSUME_DOMAINS
    ):
        return "self"

    # 2. Messaging
    if host in COMMS_DOMAINS or base in COMMS_DOMAINS:
        return "comms"

    # 3. Tools & workbench
    if host in WORK_DOMAINS or base in WORK_DOMAINS or WORK_HOST_PAT.match(host):
        return "work"

    # 4. External intake
    if host in CONSUME_DOMAINS or base in CONSUME_DOMAINS:
        return "consume"

    return "unclassified"


def bar(n, mx, width=40):
    return "#" * int(n / mx * width) if mx else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="the copied-out history.db")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--out", default=None, help="path to write the baseline JSON")
    ap.add_argument("--report", default=None,
                    help="write the full report to this file, print only a status "
                         "line to the terminal. This flag is mandatory in the "
                         "workshop flow — it's what lets the user look at the "
                         "report and delete lines before the AI ever sees it. "
                         "Without it, the report prints straight to the "
                         "terminal, and in Claude Code that means the AI has "
                         "already read the whole thing on the spot.")
    ap.add_argument("--self", dest="self_handles", default="",
                    help="confirmed personal accounts, comma-separated. "
                         "Best written as \"platform:@handle\" (e.g. "
                         "threads.com:@me,youtube.com:@MyChannel) so it only "
                         "matches that one platform; a bare \"@handle\" "
                         "matches every platform, and someone else with the "
                         "same name will get misidentified as you.")
    ap.add_argument("--with-search", action="store_true",
                    help="also output search keywords (highly sensitive, off by default)")
    ap.add_argument("--with-titles", action="store_true",
                    help="also output page titles for the external-intake "
                         "category (quality mode). Titles reveal far more "
                         "than a domain name does — this **requires separate, "
                         "explicit user consent** to turn on. Only then can "
                         "you judge whether what they're taking in is any good.")
    ap.add_argument("--exclude", default="",
                    help="keywords or domains the user named as off-limits, "
                         "comma-separated. Any matching row is dropped "
                         "entirely — not even its domain name makes it into "
                         "the report.")
    ap.add_argument("--no-auto-redact", action="store_true",
                    help="turn off the built-in sensitive-category "
                         "auto-redaction. Only use this when the user has "
                         "explicitly said \"you can see all of it.\"")
    ap.add_argument("--top", type=int, default=30)
    args = ap.parse_args()

    db = os.path.expanduser(args.db)
    if not os.path.exists(db):
        print(f"File not found: {db}", file=sys.stderr)
        print("STATUS=nofile")
        return 1

    self_handles = set()
    for raw in args.self_handles.split(","):
        raw = raw.strip().lower()
        if not raw:
            continue
        if ":" in raw:                       # threads.com:@yourname
            host_part, name = raw.split(":", 1)
            self_handles.add(f"{host_part.strip()}:@{name.strip().lstrip('@')}")
        else:                                # @yourname (matches every platform)
            self_handles.add("@" + raw.lstrip("@"))

    try:
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        rows = conn.execute(
            "select v.visit_time, v.transition, u.url, u.title "
            "from visits v join urls u on u.id = v.url"
        ).fetchall()
    except sqlite3.DatabaseError as e:
        print(f"Couldn't open this file: {e}", file=sys.stderr)
        print("STATUS=unreadable")
        return 1

    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=args.days)

    dom_visits = collections.Counter()
    dom_days = collections.defaultdict(set)
    dom_shapes = collections.defaultdict(collections.Counter)
    dom_bucket_mix = collections.defaultdict(collections.Counter)
    bucket_visits = collections.Counter()
    handle_hits = collections.defaultdict(collections.Counter)
    hours = collections.Counter()
    days = collections.Counter()
    feed_n = detail_n = 0
    total = 0
    redacted = 0
    titles = collections.defaultdict(collections.Counter)   # host -> title -> n

    extra_terms = [t.strip().lower() for t in args.exclude.split(",") if t.strip()]

    for vtime, transition, url, title in rows:
        if (transition & 0xFF) == TRANSITION_AUTO_SUBFRAME:
            continue
        # convert straight to local time, no manual timezone handling needed
        when = datetime.datetime.fromtimestamp(vtime / 1_000_000 - WEBKIT_TO_UNIX)
        if when < cutoff or when > now + datetime.timedelta(days=1):
            continue
        host, segs = split_url(url)
        if not host:
            continue

        # Sensitive or user-named-for-exclusion rows: count them and nothing else.
        # This has to happen before any other stats are gathered, to guarantee
        # a redacted domain name never leaks out through any other channel.
        if is_sensitive(host, title, extra_terms, not args.no_auto_redact):
            redacted += 1
            total += 1
            continue

        shape = path_shape(segs)
        bucket = classify(host, segs, shape, self_handles)
        h = handle_of(segs)
        if h:
            handle_hits[host][h] += 1

        total += 1
        bucket_visits[bucket] += 1
        dom_visits[host] += 1
        dom_days[host].add(when.date())
        dom_shapes[host][shape] += 1
        dom_bucket_mix[host][bucket] += 1
        hours[when.hour] += 1
        days[when.date().isoformat()] += 1

        # Feed-vs-content only gets computed for "places you scroll" — the
        # concept doesn't apply to tools/workbench or messaging.
        if bucket in ("consume", "self"):
            if shape in FEED_PATHS:
                feed_n += 1
            elif len(segs) >= 1:
                detail_n += 1

        # Titles are only collected for "external intake" visits that click
        # into a single item — that's the only case where they actually read
        # something. Titles in the feed layer are mostly just the platform's
        # own name and carry no judgment value.
        if args.with_titles and bucket == "consume" and shape not in FEED_PATHS:
            t = clean_title(title)
            if t:
                titles[host][t] += 1

    if total == 0:
        print("No history in this window. Either the day range is too short, or the wrong browser profile got picked.")
        print("STATUS=empty")
        return 0

    # ---------------- human-facing output ----------------
    # Everything gets collected into OUT first, and only afterward do we
    # decide whether to print it or write it to a file. This distinction is
    # the crux of the whole privacy promise: in Claude Code, anything that
    # gets printed is in the AI's context the instant it prints —
    # "you can delete stuff before I look" is a lie if the flow is
    # "AI runs it, then it gets printed."
    OUT = []

    def emit(line=""):
        OUT.append(line)

    emit("=" * 70)
    emit(f"Window: last {args.days} days   valid visits {total}   "
         f"spanning {len(days)} days, {len(dom_visits)} domains")
    emit("(auto-loaded embedded content filtered out; no full URLs, but page shape and handles are kept)")
    if redacted:
        emit(f"* An additional {redacted} visits ({redacted/total:.1%}) fell into a sensitive "
             f"category or a user-named exclusion, and were redacted at report-generation "
             f"time — their domain names don't appear in this report.")
    emit("=" * 70)

    emit("\n--- Where your attention went (counted per visit) ---")
    mx = max(bucket_visits.values())
    for b in BUCKETS:
        n = bucket_visits.get(b, 0)
        if not n:
            continue
        emit(f"  {LABEL[b]:<22}{n:>7}  {n/total:5.1%}  {bar(n, mx)}")

    known = feed_n + detail_n
    emit("\n--- On social & video platforms: just scrolling, or actually clicking in ---")
    if known >= 50:
        emit(f"  Stayed in feed/home/search results   {feed_n:>7}  {feed_n/known:5.1%}")
        emit(f"  Clicked into a single item           {detail_n:>7}  {detail_n/known:5.1%}")
    else:
        emit("  Too few visits of this kind to interpret this figure.")

    emit(f"\n--- Top {args.top} domains ---")
    emit(f"  {'visits':>7} {'active d':>8}  {'main type':<22} domain")
    for d, n in dom_visits.most_common(args.top):
        mix = dom_bucket_mix[d]
        main_b, main_n = mix.most_common(1)[0]
        tag = LABEL[main_b]
        if len(mix) > 1 and main_n / n < 0.8:
            tag += " (mixed)"
        emit(f"  {n:>7} {len(dom_days[d]):>8}  {tag:<22} {d}")

    emit("\n--- What you're looking at on your top domains (path shape) ---")
    for d, n in dom_visits.most_common(8):
        mix = " / ".join(f"{LABEL[b]} {c}" for b, c in dom_bucket_mix[d].most_common(3))
        emit(f"  [{d}]  {n} visits total   -> {mix}")
        for shape, sn in dom_shapes[d].most_common(5):
            emit(f"      {sn:>6}  {shape}")

    emit("\n--- Likely \"personal account\" candidates (confirm with the user, don't assume) ---")
    found = False
    for host, hs in sorted(handle_hits.items(), key=lambda kv: -sum(kv[1].values())):
        top = hs.most_common(3)
        if not top or top[0][1] < 10:
            continue
        others = sum(v for _, v in top[1:])
        if top[0][1] >= max(10, others * 2):
            emit(f"  {host}: {top[0][0]}"
                 f" ({top[0][1]} visits; other accounts on this platform total {others})")
            found = True
    if not found:
        emit("  No clear candidate found.")
    emit("  Once confirmed, rerun with --self <handle> so the \"watching yourself\" column is accurate.")

    emit("\n--- Time-of-day distribution (local time) ---")
    mxh = max(hours.values())
    for h in range(24):
        n = hours.get(h, 0)
        emit(f"  {h:02d}:00  {n:>6}  {bar(n, mxh, 46)}")
    night = sum(hours.get(h, 0) for h in (0, 1, 2, 3, 4))
    emit(f"  Total for 00:00-05:00: {night} visits ({night/total:.1%})")

    unc = bucket_visits.get("unclassified", 0)
    if unc:
        emit(f"\n--- Unclassified domains ({unc} visits, {unc/total:.1%}) ---")
        emit("  These fall outside the built-in list. Local news, niche forums, and")
        emit("  non-English platforms will always land here — that's expected, not a bug.")
        emit("  Please work through these with the user to figure out which bucket they belong in:")
        shown = 0
        for d, n in dom_visits.most_common(200):
            if dom_bucket_mix[d].most_common(1)[0][0] != "unclassified":
                continue
            emit(f"      {n:>6}  {d}")
            shown += 1
            if shown >= 15:
                break

    if args.with_titles:
        emit("\n--- What they actually read (quality mode, only reached after separate user consent) ---")
        emit("  Only collects titles of \"external intake\" pages clicked into individually; feed-layer visits are excluded.")
        emit("  When judging quality, look for: titles that are uniformly emotional or clickbaity, whether")
        emit("  topics are concentrated or scattered, and whether anything looks like it takes real time to")
        emit("  read. Criteria in references/quality-review.md.")
        shown_hosts = 0
        for host, tc in sorted(titles.items(), key=lambda kv: -sum(kv[1].values())):
            if sum(tc.values()) < 3:
                continue
            emit(f"\n  [{host}]  {sum(tc.values())} visits")
            for t, tn in tc.most_common(12):
                mark = f" x{tn}" if tn > 1 else ""
                emit(f"      {t[:90]}{mark}")
            shown_hosts += 1
            if shown_hosts >= 8:
                break
        if not shown_hosts:
            emit("  Not enough single-item reads to judge — and that absence is itself a finding.")

    if args.with_search:
        emit("\n--- Search keywords (highly sensitive, only reached after explicit user consent) ---")
        try:
            for (term,) in conn.execute(
                "select term from keyword_search_terms order by rowid desc limit 60"
            ):
                emit(f"  {term}")
        except sqlite3.DatabaseError:
            emit("  This browser doesn't store search keywords.")

    # The report either gets written to a file (user reviews and redacts
    # first, AI reads it afterward) or printed directly.
    if args.report:
        rp = os.path.expanduser(args.report)
        os.makedirs(os.path.dirname(rp) or ".", exist_ok=True)
        with open(rp, "w", encoding="utf-8") as f:
            f.write("\n".join(OUT) + "\n")
        print(f"Report written to: {rp}")
        print(f"{len(OUT)} lines total. The content isn't printed here — that's intentional.")
        print("Next: ask the user what they don't want analyzed, use redact.py to drop "
              "those lines by keyword, and only read this file after that.")
        print("REPORT_WRITTEN=1")
    else:
        print("\n".join(OUT))

    # ---------------- machine-facing baseline ----------------
    baseline = {
        "generated_at": now.isoformat(timespec="seconds"),
        "window_days": args.days,
        "total_visits": total,
        "days_covered": len(days),
        "buckets": {b: bucket_visits.get(b, 0) for b in BUCKETS},
        "feed_visits": feed_n,
        "detail_visits": detail_n,
        "late_night_visits": night,
        "top_domains": [
            {"domain": d, "visits": n, "active_days": len(dom_days[d]),
             "bucket": dom_bucket_mix[d].most_common(1)[0][0]}
            for d, n in dom_visits.most_common(args.top)
        ],
        "hours": {str(h): hours.get(h, 0) for h in range(24)},
    }
    if args.out:
        out = os.path.expanduser(args.out)
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(baseline, f, ensure_ascii=False, indent=2)
        print(f"\nBaseline saved to: {out}")
        print("(rerun later and compare against this to see whether anything actually changed)")

    print("\nSTATUS=ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
