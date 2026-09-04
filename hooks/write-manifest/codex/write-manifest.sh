#!/usr/bin/env bash
set -euo pipefail
umask 077
# write-manifest.sh (Codex build)
#
# PostToolUse[apply_patch|Write|Edit|MultiEdit] -- appends every file path
# this turn's edit tools touched to a per-session write-manifest. This is
# the ground truth a later checkpoint/closure step reads to know which
# files "this session" is responsible for, as opposed to a file another
# session left dirty in the same working tree. Silent by design: no stdout,
# zero context cost.
#
# id chain: Codex payloads may carry session_id / thread_id / turn_id --
# prefer whichever one is stable across the whole session, not just the turn.
#
# Known asymmetry vs. the Claude Code build in the neighboring folder: this
# one only tracks *which paths* were touched. It does not also log old/new
# content pairs the way write-manifest.sh does on the Claude Code side, so
# there is no Codex equivalent of stage-own-edits.sh (reconstructing "HEAD +
# only this session's edits" for a file another session also modified).
# apply_patch's payload is a unified-diff-shaped patch, not a clean
# old_string/new_string pair, so replaying just this session's hunks needs
# more parsing than this hook does today. If a file is dirty from another
# session, the safest move on Codex is still to hold it for a human, not to
# stage the whole thing.

input="$(cat)"
tool="$(printf '%s' "$input" | jq -r '.tool_name // ""')"
sid="$(printf '%s' "$input" | jq -r '.session_id // .thread_id // .turn_id // ""')"
cwd="$(printf '%s' "$input" | jq -r '.cwd // ""')"
[ -z "$sid" ] && exit 0
[[ "$sid" =~ ^[A-Za-z0-9_-]{8,128}$ ]] || exit 0

case "$tool" in
  Write|Edit|MultiEdit|apply_patch|Bash|exec|shell) ;;
  *) exit 0 ;;
esac

paths=""
fp="$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.path // .tool_input.notebook_path // ""')"
if [ -n "$fp" ]; then
  paths="$fp"
else
  # apply_patch as a dedicated tool carries the patch in tool_input; Codex exec
  # mode instead runs `apply_patch <<'EOF'` through the shell channel, so the
  # patch body (with its "*** Update File:" lines) sits inside .command.
  content="$(printf '%s' "$input" | jq -r 'if (.tool_input | type) == "string" then .tool_input else (.tool_input.patch // .tool_input.input // .tool_input.command // "") end')"
  case "$tool" in
    Bash|exec|shell)
      printf '%s' "$content" | grep -q 'apply_patch' || exit 0 ;;
  esac
  paths="$(printf '%s\n' "$content" | sed -nE 's/^\*\*\* (Add|Update|Delete) File: //p' || true)"
fi
[ -z "$paths" ] && exit 0

dir="$HOME/.codex/state/write-manifests"
mkdir -p "$dir"
chmod 700 "$HOME/.codex/state" "$dir" 2>/dev/null || true
list="$dir/$sid.list"
[[ -L "$list" ]] && exit 0
touch "$list"
chmod 600 "$list" 2>/dev/null || true
while IFS= read -r p; do
  [ -z "$p" ] && continue
  case "$p" in
    /*) ;;
    ~/*) p="$HOME/${p#~/}" ;;
    *) p="${cwd:-$PWD}/$p" ;;
  esac
  grep -qxF -- "$p" "$list" 2>/dev/null || printf '%s\n' "$p" >> "$list"
done <<EOF
$paths
EOF
exit 0
