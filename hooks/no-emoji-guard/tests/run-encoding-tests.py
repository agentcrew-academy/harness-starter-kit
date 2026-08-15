#!/usr/bin/env python3
"""Regression test: no-emoji-guard must work when stdin is not UTF-8.

    python hooks/no-emoji-guard/tests/run-encoding-tests.py

Why this exists. `json.load(sys.stdin)` decodes using whatever encoding the
locale gives the process. On a Windows install whose locale is not UTF-8 --
the default for Traditional Chinese (cp950), Japanese (cp932) and Korean
(cp949) systems -- stdin arrives as that legacy codec with the
surrogateescape error handler. Emoji are by definition non-ASCII, so every
emoji in the payload is turned into unpaired surrogates before the hook ever
looks at it. find_emoji() then finds nothing, and the hook allows the write.

It does not error. It does not warn. It reports success while blocking
nothing, which is the one failure mode this kit exists to prevent.

You do not need a Chinese Windows machine to see it: the tests below set
PYTHONIOENCODING explicitly, so they reproduce the condition on any platform.
Each case runs twice, once under utf-8 and once under cp950, so the utf-8 row
shows the hook still behaves the same where it always worked.

Expected: 6 passed, 0 failed.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "claude-code" / "no-emoji-guard.py"

# (label, content, must_block)
CASES = [
    ("ASCII text with an emoji", "ship it \U0001F680", True),
    ("non-ASCII text with an emoji", "完成 \U0001F680", True),
    ("clean ASCII text", "ship it", False),
]

ENCODINGS = ["utf-8", "cp950"]


def run(content, encoding):
    payload = json.dumps(
        {"tool_name": "Write", "tool_input": {"file_path": "note.md", "content": content}},
        ensure_ascii=False,
    ).encode("utf-8")
    env = dict(os.environ, PYTHONIOENCODING=encoding)
    return subprocess.run(
        [sys.executable, str(HOOK)], input=payload, capture_output=True, env=env
    ).returncode


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    if not HOOK.exists():
        print("hook not found: %s" % HOOK)
        return 1

    failures = 0
    for encoding in ENCODINGS:
        for label, content, must_block in CASES:
            code = run(content, encoding)
            blocked = code == 2
            ok = blocked == must_block
            failures += not ok
            print(
                "%-4s PYTHONIOENCODING=%-6s %-30s expected=%s got=%s%s"
                % (
                    "PASS" if ok else "FAIL",
                    encoding,
                    label,
                    "block" if must_block else "allow",
                    "block" if blocked else "allow",
                    "" if code in (0, 2) else " (exit %d)" % code,
                )
            )

    print("\nfailures: %d" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
