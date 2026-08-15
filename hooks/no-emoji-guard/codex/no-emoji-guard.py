#!/usr/bin/env python3
"""
codex-no-emoji-guard.py (Codex PreToolUse: Write|Edit|MultiEdit|apply_patch)

Blocks emoji in written content. Global rule: no emoji in external or internal
documents.

Criteria (per Unicode UTS #51 emoji-data.txt v17.0, official file dated 2025-07-25):
  1. Characters with Emoji_Presentation=Yes -- rendered as colored emoji by
     default (e.g. checkmark, X, hourglass, fast-forward, lock)
  2. Extended_Pictographic characters followed by VS16 (U+FE0F) -- explicitly
     requested to render as emoji (e.g. warning sign with the color marker)

Deliberately NOT blocked (these are typographic symbols, not emoji, and are
used in brand styling): checkmark, X mark, arrows (up/down/left/right), and
(C) (R) (TM) when not followed by VS16

Source: https://www.unicode.org/Public/UCD/latest/ucd/emoji/emoji-data.txt
Update method: re-run the parser against that file and replace the two tables below.
"""
import json
import os
import re
import sys

EMOJI_PRESENTATION=[(0x231a,0x231b),(0x23e9,0x23ec),(0x23f0,0x23f0),(0x23f3,0x23f3),(0x25fd,0x25fe),(0x2614,0x2615),(0x2648,0x2653),(0x267f,0x267f),(0x2693,0x2693),(0x26a1,0x26a1),(0x26aa,0x26ab),(0x26bd,0x26be),(0x26c4,0x26c5),(0x26ce,0x26ce),(0x26d4,0x26d4),(0x26ea,0x26ea),(0x26f2,0x26f3),(0x26f5,0x26f5),(0x26fa,0x26fa),(0x26fd,0x26fd),(0x2705,0x2705),(0x270a,0x270b),(0x2728,0x2728),(0x274c,0x274c),(0x274e,0x274e),(0x2753,0x2755),(0x2757,0x2757),(0x2795,0x2797),(0x27b0,0x27b0),(0x27bf,0x27bf),(0x2b1b,0x2b1c),(0x2b50,0x2b50),(0x2b55,0x2b55),(0x1f004,0x1f004),(0x1f0cf,0x1f0cf),(0x1f18e,0x1f18e),(0x1f191,0x1f19a),(0x1f1e6,0x1f1ff),(0x1f201,0x1f201),(0x1f21a,0x1f21a),(0x1f22f,0x1f22f),(0x1f232,0x1f236),(0x1f238,0x1f23a),(0x1f250,0x1f251),(0x1f300,0x1f320),(0x1f32d,0x1f335),(0x1f337,0x1f37c),(0x1f37e,0x1f393),(0x1f3a0,0x1f3ca),(0x1f3cf,0x1f3d3),(0x1f3e0,0x1f3f0),(0x1f3f4,0x1f3f4),(0x1f3f8,0x1f43e),(0x1f440,0x1f440),(0x1f442,0x1f4fc),(0x1f4ff,0x1f53d),(0x1f54b,0x1f54e),(0x1f550,0x1f567),(0x1f57a,0x1f57a),(0x1f595,0x1f596),(0x1f5a4,0x1f5a4),(0x1f5fb,0x1f64f),(0x1f680,0x1f6c5),(0x1f6cc,0x1f6cc),(0x1f6d0,0x1f6d2),(0x1f6d5,0x1f6d8),(0x1f6dc,0x1f6df),(0x1f6eb,0x1f6ec),(0x1f6f4,0x1f6fc),(0x1f7e0,0x1f7eb),(0x1f7f0,0x1f7f0),(0x1f90c,0x1f93a),(0x1f93c,0x1f945),(0x1f947,0x1f9ff),(0x1fa70,0x1fa7c),(0x1fa80,0x1fa8a),(0x1fa8e,0x1fac6),(0x1fac8,0x1fac8),(0x1facd,0x1fadc),(0x1fadf,0x1faea),(0x1faef,0x1faf8)]
EXT_PICTOGRAPHIC=[(0xa9,0xa9),(0xae,0xae),(0x203c,0x203c),(0x2049,0x2049),(0x2122,0x2122),(0x2139,0x2139),(0x2194,0x2199),(0x21a9,0x21aa),(0x231a,0x231b),(0x2328,0x2328),(0x23cf,0x23cf),(0x23e9,0x23f3),(0x23f8,0x23fa),(0x24c2,0x24c2),(0x25aa,0x25ab),(0x25b6,0x25b6),(0x25c0,0x25c0),(0x25fb,0x25fe),(0x2600,0x2604),(0x260e,0x260e),(0x2611,0x2611),(0x2614,0x2615),(0x2618,0x2618),(0x261d,0x261d),(0x2620,0x2620),(0x2622,0x2623),(0x2626,0x2626),(0x262a,0x262a),(0x262e,0x262f),(0x2638,0x263a),(0x2640,0x2640),(0x2642,0x2642),(0x2648,0x2653),(0x265f,0x2660),(0x2663,0x2663),(0x2665,0x2666),(0x2668,0x2668),(0x267b,0x267b),(0x267e,0x267f),(0x2692,0x2697),(0x2699,0x2699),(0x269b,0x269c),(0x26a0,0x26a1),(0x26a7,0x26a7),(0x26aa,0x26ab),(0x26b0,0x26b1),(0x26bd,0x26be),(0x26c4,0x26c5),(0x26c8,0x26c8),(0x26ce,0x26cf),(0x26d1,0x26d1),(0x26d3,0x26d4),(0x26e9,0x26ea),(0x26f0,0x26f5),(0x26f7,0x26fa),(0x26fd,0x26fd),(0x2702,0x2702),(0x2705,0x2705),(0x2708,0x270d),(0x270f,0x270f),(0x2712,0x2712),(0x2714,0x2714),(0x2716,0x2716),(0x271d,0x271d),(0x2721,0x2721),(0x2728,0x2728),(0x2733,0x2734),(0x2744,0x2744),(0x2747,0x2747),(0x274c,0x274c),(0x274e,0x274e),(0x2753,0x2755),(0x2757,0x2757),(0x2763,0x2764),(0x2795,0x2797),(0x27a1,0x27a1),(0x27b0,0x27b0),(0x27bf,0x27bf),(0x2934,0x2935),(0x2b05,0x2b07),(0x2b1b,0x2b1c),(0x2b50,0x2b50),(0x2b55,0x2b55),(0x3030,0x3030),(0x303d,0x303d),(0x3297,0x3297),(0x3299,0x3299),(0x1f004,0x1f004),(0x1f02c,0x1f02f),(0x1f094,0x1f09f),(0x1f0af,0x1f0b0),(0x1f0c0,0x1f0c0),(0x1f0cf,0x1f0d0),(0x1f0f6,0x1f0ff),(0x1f170,0x1f171),(0x1f17e,0x1f17f),(0x1f18e,0x1f18e),(0x1f191,0x1f19a),(0x1f1ae,0x1f1e5),(0x1f201,0x1f20f),(0x1f21a,0x1f21a),(0x1f22f,0x1f22f),(0x1f232,0x1f23a),(0x1f23c,0x1f23f),(0x1f249,0x1f25f),(0x1f266,0x1f321),(0x1f324,0x1f393),(0x1f396,0x1f397),(0x1f399,0x1f39b),(0x1f39e,0x1f3f0),(0x1f3f3,0x1f3f5),(0x1f3f7,0x1f3fa),(0x1f400,0x1f4fd),(0x1f4ff,0x1f53d),(0x1f549,0x1f54e),(0x1f550,0x1f567),(0x1f56f,0x1f570),(0x1f573,0x1f57a),(0x1f587,0x1f587),(0x1f58a,0x1f58d),(0x1f590,0x1f590),(0x1f595,0x1f596),(0x1f5a4,0x1f5a5),(0x1f5a8,0x1f5a8),(0x1f5b1,0x1f5b2),(0x1f5bc,0x1f5bc),(0x1f5c2,0x1f5c4),(0x1f5d1,0x1f5d3),(0x1f5dc,0x1f5de),(0x1f5e1,0x1f5e1),(0x1f5e3,0x1f5e3),(0x1f5e8,0x1f5e8),(0x1f5ef,0x1f5ef),(0x1f5f3,0x1f5f3),(0x1f5fa,0x1f64f),(0x1f680,0x1f6c5),(0x1f6cb,0x1f6d2),(0x1f6d5,0x1f6e5),(0x1f6e9,0x1f6e9),(0x1f6eb,0x1f6f0),(0x1f6f3,0x1f6ff),(0x1f7da,0x1f7ff),(0x1f80c,0x1f80f),(0x1f848,0x1f84f),(0x1f85a,0x1f85f),(0x1f888,0x1f88f),(0x1f8ae,0x1f8af),(0x1f8bc,0x1f8bf),(0x1f8c2,0x1f8cf),(0x1f8d9,0x1f8ff),(0x1f90c,0x1f93a),(0x1f93c,0x1f945),(0x1f947,0x1f9ff),(0x1fa58,0x1fa5f),(0x1fa6e,0x1faff),(0x1fc00,0x1fffd)]

VS16 = 0xFE0F

# Obsidian Tasks plugin functional markers (only allowed on to-do lines: - [ ] / - [x])
TASK_MARKERS = re.compile(
    "[" +
    "\U0001F4C5"  # due date
    "\U0001F4C6"  # scheduled
    "\U0001F6EB"  # start
    "\u2705"      # done
    "\u274C"      # cancelled
    "\u23F3"      # in progress
    "\U0001F501"  # recurring
    "\u23EB\u23EC\U0001F53C\U0001F53D"  # priority
    "\U0001F525\u23F1\U0001F534"          # daily-note convention symbols
    "]\uFE0F?"
)



def read_payload():
    """Read the hook payload as bytes and decode UTF-8 explicitly.

    `json.load(sys.stdin)` decodes using whatever encoding the locale hands the
    process. Where that is not UTF-8 -- the default on a Chinese, Japanese, or
    Korean Windows install -- any non-ASCII text in the payload is mangled, the
    JSON fails to parse, and the hook fails open. Silently, and precisely when
    the message or the command is not in English.

    Observed in service on 2026-08-15: a 2.3 KB Stop payload parsed as an empty
    object, so claim-evidence-guard saw no assistant message and let the turn
    end. Reading bytes removes the dependency on the ambient locale entirely.
    """
    raw = sys.stdin.buffer.read()
    if not raw.strip():
        return {}
    return json.loads(raw.decode("utf-8", "replace"))


def _in(cp, table):
    for a, b in table:
        if a <= cp <= b:
            return True
        if cp < a:
            return False
    return False


def find_emoji(text):
    """Return [(char, position)] per the two criteria above."""
    hits = []
    n = len(text)
    for i, ch in enumerate(text):
        cp = ord(ch)
        if _in(cp, EMOJI_PRESENTATION):
            hits.append((ch, i))
        elif _in(cp, EXT_PICTOGRAPHIC) and i + 1 < n and ord(text[i + 1]) == VS16:
            hits.append((ch + text[i + 1], i))
    return hits


# To exempt an entire subtree (e.g. an Obsidian vault, where these symbols are
# functional syntax rather than decoration), add the path fragment here.
# Example: EXEMPT_PATH_SUBSTRINGS = ["/my-notes/", "/vault/"]
EXEMPT_PATH_SUBSTRINGS = []


def _exempt_subtree(path):
    return any(s and s in path for s in EXEMPT_PATH_SUBSTRINGS)


def collect(tool_input):
    """Gather all the text content being written this call (field names vary by tool)."""
    parts = []
    for key in ("content", "new_string", "prompt", "patch", "input"):
        v = tool_input.get(key)
        if isinstance(v, str):
            parts.append(v)
    for edit in tool_input.get("edits", []) or []:
        if isinstance(edit, dict) and isinstance(edit.get("new_string"), str):
            parts.append(edit["new_string"])
    return "\n".join(parts)


def main():
    try:
        payload = read_payload()
    except Exception:
        sys.exit(0)

    tool_name = payload.get("tool_name") or ""
    if tool_name not in {"Write", "Edit", "MultiEdit", "apply_patch", "Bash", "exec", "shell"}:
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    if isinstance(tool_input, str):
        tool_input = {"patch": tool_input}

    exempt_path = r"(逐字稿|transcript|/_archive/|\.srt$|\.vtt$)"

    if tool_name in {"Bash", "exec", "shell"}:
        # codex exec mode runs apply_patch as a shell command, with the patch body in `command`.
        # Only added lines are scanned -- scanning the whole diff would also block a patch that
        # is removing emoji.
        command = tool_input.get("command") or ""
        if "apply_patch" not in command:
            sys.exit(0)
        cwd = payload.get("cwd") or ""
        patch_paths = [
            p if os.path.isabs(p) else os.path.join(cwd, p)
            for p in re.findall(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", command, flags=re.M)
        ]
        if patch_paths and all(
            re.search(exempt_path, p) or _exempt_subtree(p) for p in patch_paths
        ):
            sys.exit(0)
        text = "\n".join(
            line[1:] for line in command.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
    else:
        path = tool_input.get("file_path") or tool_input.get("path") or ""

        # Transcripts and raw external input being archived as-is are not blocked
        if re.search(exempt_path, path):
            sys.exit(0)

        # Exempt the whole subtree (see EXEMPT_PATH_SUBSTRINGS above). The typical
        # use case is an Obsidian vault: due-date/completion/in-progress markers
        # there are functional Tasks plugin syntax, not decoration, and stripping
        # them would break to-do tracking.
        if _exempt_subtree(path):
            sys.exit(0)

        text = collect(tool_input)

    if not text:
        sys.exit(0)

    # Obsidian to-do lines (- [ ] / - [x]) in any file also get the above
    # Tasks plugin markers exempted
    text = re.sub(
        r"^(\s*[-*]\s*\[[ xX/\-]\].*)$",
        lambda m: TASK_MARKERS.sub("", m.group(1)),
        text,
        flags=re.M,
    )

    hits = find_emoji(text)
    if not hits:
        sys.exit(0)

    uniq = []
    for ch, _ in hits:
        if ch not in uniq:
            uniq.append(ch)

    sys.stderr.write(
        "NO-EMOJI GUARD: this write contains %d emoji%s -- %s\n"
        "Global rule: no emoji in documents, slides, code comments, or commit messages.\n"
        "Remove them and rewrite. For status symbols, use typographic marks (checkmark, X, arrows) or plain text (done/todo/note) instead.\n"
        "Exemptions (transcripts, raw external files being archived) are auto-allowed and this write is not one of them.\n"
        % (len(hits), " (%d unique after dedup)" % len(uniq) if len(uniq) != len(hits) else "", " ".join(uniq))
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
