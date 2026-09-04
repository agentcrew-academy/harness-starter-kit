#!/bin/bash
# stage-own-edits.sh <session-id> <file> [<file> ...]
#
# For a file that another session may also have modified, stage ONLY this
# session's edits: take the HEAD version, replay the Edit old->new pairs recorded
# in ~/.claude/state/edit-logs/<sid>.jsonl, write the result straight into the
# index (hash-object + update-index). The working tree is never touched, so the
# other session's uncommitted content stays exactly where it is.
#
# Exit codes per file (printed as "<code> <file> <reason>"):
#   0  staged                      index = HEAD + my edits
#   1  identical-to-worktree       nobody else touched it; plain `git add` done instead
#   2  hold: whole-file write      this session used Write on it — cannot separate edits
#   3  hold: edit not found in HEAD an old_string no longer matches HEAD (overlapping change)
#   4  hold: no edits logged       file not in this session's edit log
#   5  error                       not in a git repo / HEAD has no such path
# Overall exit = highest per-file code.

set -u
SID="${1:?session id}"; shift
LOG="$HOME/.claude/state/edit-logs/$SID.jsonl"
[ -f "$LOG" ] || { echo "4 - no edit log for session $SID"; exit 4; }

worst=0
for FILE in "$@"; do
  ABS=$(cd "$(dirname "$FILE")" 2>/dev/null && pwd -P)/$(basename "$FILE")
  ROOT=$(git -C "$(dirname "$ABS")" rev-parse --show-toplevel 2>/dev/null) || { echo "5 $FILE not in a git repo"; worst=5; continue; }
  REL=${ABS#"$ROOT"/}
  OUT=$(python3 - "$LOG" "$ABS" "$ROOT" "$REL" <<'PY'
import json, subprocess, sys
log, abs_path, root, rel = sys.argv[1:5]
edits = [json.loads(l) for l in open(log) if l.strip()]
mine = [e for e in edits if e.get("f") == abs_path]
if not mine:
    print("4 hold: no edits logged"); sys.exit(0)
if any(e.get("op") == "write" for e in mine):
    print("2 hold: whole-file write"); sys.exit(0)
r = subprocess.run(["git", "-C", root, "show", f"HEAD:{rel}"], capture_output=True)
if r.returncode != 0:
    print("5 error: path not in HEAD"); sys.exit(0)
content = r.stdout.decode("utf-8")
for e in mine:
    old, new = e["old"], e["new"]
    if old not in content:
        print("3 hold: edit not found in HEAD"); sys.exit(0)
    content = content.replace(old, new) if e.get("all") else content.replace(old, new, 1)
try:
    wt = open(abs_path, encoding="utf-8").read()
except FileNotFoundError:
    wt = None
if wt == content:
    print("1 identical-to-worktree"); sys.exit(0)
sha = subprocess.run(["git", "-C", root, "hash-object", "-w", "--stdin"], input=content.encode("utf-8"), capture_output=True, check=True).stdout.decode().strip()
mode = subprocess.run(["git", "-C", root, "ls-files", "-s", "--", rel], capture_output=True).stdout.decode().split()
m = mode[0] if mode else "100644"
subprocess.run(["git", "-C", root, "update-index", "--cacheinfo", f"{m},{sha},{rel}"], check=True)
print("0 staged")
PY
)
  code=${OUT%% *}
  case "$code" in
    1) git -C "$ROOT" add -- "$REL" ;;
  esac
  echo "$code $FILE ${OUT#* }"
  [ "$code" -gt "$worst" ] && worst=$code
done
exit "$worst"
